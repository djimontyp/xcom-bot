import random

import discord
from discord import Cog, ApplicationContext, SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import Bot, cooldown

import src.core.utils
from src.core import database
from src.core.checks import is_user_in_db
from src.core.config import settings
from src.errors.player import NotSetRolesError, PlayerNotCreatedError, PlayerNotInSearchError, PlayerSelfInviteError
from src.core.models import Player
from src.core.enum import Rank, Map
from src.services.roles import RolesService
from src.components.views.confirm import Confirm
from src.components.views.game_result import ResultsButtons


class PlayerCog(Cog, guild_ids=[settings.GUILD_ID]):
    def __init__(self, bot: Bot):
        self.bot = bot

    player = SlashCommandGroup("player", "Группа команд для игроков.")

    @player.command()
    async def start(self, ctx: ApplicationContext):
        await ctx.defer()  # Что бы не было ошибки если команда выполняется дольше 3 секунд.

        # Проверка на наличие игрока в базе данных.
        if player := database.players.get(ctx.user.id):
            await ctx.respond("Игрок уже создан.", embed=player.embed)
            return

        # С чем будем работать
        roles_service = RolesService()
        player = Player(id=ctx.user.id)
        if not (neofit := roles_service.get_role(ctx, Rank.neofit)):
            await ctx.respond("Неофит роль не установлена. Обратитесь к администратору.")
            return

        # Сам процесс
        database.players.update({ctx.user.id: player})
        await ctx.user.add_roles(neofit)

        await ctx.respond("Игрок создан.", embed=player.embed, delete_after=settings.DELETE_AFTER, ephemeral=True)

    @player.command(description="Начать поиск игры.")
    @is_user_in_db()
    async def go(self, ctx: ApplicationContext):
        await ctx.defer()

        player = database.players[ctx.user.id]
        player.in_search = True
        await ctx.respond("Поиск начат.", embed=player.embed, delete_after=settings.DELETE_AFTER, ephemeral=True)

    @player.command(description="Остановить поиск игры.")
    @is_user_in_db()
    async def leave(self, ctx: ApplicationContext):
        await ctx.defer()

        player = database.players[ctx.user.id]
        player.in_search = False
        await ctx.respond("Поиск остановлен.", embed=player.embed, delete_after=settings.DELETE_AFTER, ephemeral=True)

    @player.command(description="Пригласить игрока в сессию.")
    @cooldown(1, settings.INVITE_COOLDOWN, commands.BucketType.user)
    @is_user_in_db()
    async def invite(self, ctx: ApplicationContext, player: discord.Member):
        await ctx.defer()
        await ctx.respond(f"Ожидаем ответа от {player.mention}.", ephemeral=True)

        if player.id not in database.players:
            raise PlayerNotCreatedError()
        elif not database.players[player.id].in_search:
            raise PlayerNotInSearchError()
        # elif player.id == ctx.user.id:
        #     raise PlayerSelfInviteError()

        view = Confirm(initiator=ctx.user.id, invited=player.id)
        if player.can_send():
            private = await player.send(f"{ctx.user.mention} приглашает {player.mention} в сессию.", view=view)
            await view.wait()
            await private.edit(view=view)
            # TODO Логика ожидания записьвать в бд
            # initiator, invited = database.players[ctx.user.id], database.players[player.id]

            if view.value:
                msg = f"{player.mention} принял приглашение."
                category = discord.utils.get(ctx.guild.categories, id=1144222416919339048)  # TODO

                if not category:
                    await ctx.respond(
                        f"Категория для сессии не найдена.", delete_after=settings.DELETE_AFTER, ephemeral=True
                    )
                else:
                    overwrites = {
                        ctx.guild.default_role: discord.PermissionOverwrite(connect=False),
                        ctx.guild.me: discord.PermissionOverwrite(connect=True),
                        player: discord.PermissionOverwrite(connect=True),
                    }
                    voice_title = "{} vs {}".format(ctx.user.display_name, player.display_name)
                    voice = await category.create_voice_channel(name=voice_title, overwrites=overwrites)

                    buttons = ResultsButtons(initiator_id=ctx.user.id, invited_id=player.id)
                    await voice.send(view=buttons)

                    database.players[ctx.user.id].in_search, database.players[player.id].in_search = False, False

                    map_ = random.choice(list(Map))
                    await player.send(f"Приглашение в сессию от {ctx.user.mention}. Карта: {map_}.\n{voice.jump_url}")
                    await ctx.user.send(f"Приглашение в сессию для {player.mention}. Карта: {map_}.\n{voice.jump_url}")
            elif view.value is None:
                msg = f"{player.mention} не ответил на приглашение."
            else:
                msg = f"{player.mention} отклонил приглашение."

            await ctx.respond(msg, delete_after=settings.DELETE_AFTER, ephemeral=True)
            await ctx.delete()
        else:
            await ctx.respond(f"{player.mention} не может получать личные сообщения.", ephemeral=True)

    async def cog_check(self, ctx: ApplicationContext):
        """Проверка на наличие ролей соответствия для всего модуля игроков."""

        if not all(src.core.utils.roles_ids__mapper.values()):
            raise NotSetRolesError()

        return True

    async def cog_command_error(self, ctx: ApplicationContext, error: Exception) -> None:
        """Обработка ошибок для модуля игроков."""
        if isinstance(error, NotSetRolesError):
            admin_cog = self.bot.get_cog("AdminCog")
            admin_commands = discord.utils.get(admin_cog.get_commands(), name="admin")
            set_roles = discord.utils.get(admin_commands.walk_commands(), name="set_roles")  # noqa
            await ctx.respond(
                f"{str(error)}\n{set_roles.mention}.",
                ephemeral=True,
                delete_after=settings.DELETE_AFTER,
            )
        elif isinstance(error, (PlayerNotInSearchError, PlayerSelfInviteError)):
            await ctx.respond(
                str(error),
                ephemeral=True,
                delete_after=settings.DELETE_AFTER,
            )
        elif isinstance(error, PlayerNotCreatedError):
            player_commands = discord.utils.get(self.get_commands(), name="player")
            start = discord.utils.get(player_commands.walk_commands(), name="start")  # noqa
            await ctx.respond(
                f"{str(error)} Регистрация в боте: {start.mention}.",
                ephemeral=True,
                delete_after=settings.DELETE_AFTER,
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(
                f"Защита от спама. Попробуй еще раз через {error.retry_after:.2f} секунд.",
                ephemeral=True,
                delete_after=settings.DELETE_AFTER,
            )
        else:
            print(error)
            await ctx.respond(
                f"Модуль игроков: Произошла неизвестная ошибка.",
                ephemeral=True,
                delete_after=settings.DELETE_AFTER,
            )
