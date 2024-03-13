import random

import discord
from discord import Cog, ApplicationContext, SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import Bot, cooldown
from discord.utils import get
from sqlalchemy import select, func

from src.components.views.confirm import Confirm
from src.components.views.game_result import ResultsButtons
from src.core.checks import is_user_in_db
from src.core.config import settings
from src.core.database import async_session_maker
from src.core.enum import Rank, Map
from src.core.models import Player
from src.core.utils import roles_ids
from src.errors.player import (
    NotSetRolesError,
    PlayerNotCreatedError,
    PlayerNotInSearchError,
    PlayerSelfInviteError,
    PlayerAlreadyCreatedError,
)
from src.services.player import PlayerService


class PlayerCog(Cog, guild_ids=[settings.GUILD_ID]):
    def __init__(self, bot: Bot):
        self.bot = bot

    player = SlashCommandGroup("player", "Группа команд для игроков.")

    @player.command(description="Регистрация в боте.")
    async def start(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)

        async with PlayerService(ctx.user.id, ctx=ctx) as service:
            if player := await service.get_instance():
                raise PlayerAlreadyCreatedError(player)

            await service.add(Player(id=ctx.user.id))
            await service.session.commit()

        embed = await service.get_player_embed()
        role = ctx.guild.get_role(roles_ids[Rank.neofit])
        await ctx.user.add_roles(role)
        await ctx.respond("Игрок создан.", embed=embed, delete_after=settings.DELETE_AFTER, ephemeral=True)

    @player.command(description="Начать поиск игры.")
    @is_user_in_db()
    async def go(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)

        async with PlayerService(ctx.user.id, ctx=ctx) as service:
            async with service.session.begin():
                player = await service.get_instance()
                player.in_search = True
            embed = await service.get_player_embed()

        await ctx.respond("Поиск начат.", embed=embed, delete_after=settings.DELETE_AFTER, ephemeral=True)

    @player.command(description="Остановить поиск игры.")
    @is_user_in_db()
    async def leave(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)

        async with PlayerService(ctx.user.id, ctx=ctx) as service:
            async with service.session.begin():
                player = await service.get_instance()
                player.in_search = False
            embed = await service.get_player_embed()

        await ctx.respond("Поиск остановлен.", embed=embed, delete_after=settings.DELETE_AFTER, ephemeral=True)

    @player.command(description="История игр")
    @is_user_in_db()
    async def history(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)
        async with PlayerService(ctx.user.id, ctx=ctx) as service:
            games = await service.get_my_last_10_games()

        embed = discord.Embed(title=f"Последние 10 игр", color=discord.Color.red())
        description = ""
        for game in games:
            winner = get(self.bot.get_all_members(), id=game.winner_id)
            loser = get(self.bot.get_all_members(), id=game.loser_id)
            if not loser or not winner:
                continue

            description += f"`№{str(game.id).rjust(4, ' ')}.`"
            description += f" 🏆{winner.mention}"
            description += f" `{game.winner_rating_before}`⮕`{game.winner_rating_after}[{game.winner_income}]`"
            description += f" "
            description += f"😮‍💨{loser.mention}"
            description += f" `{game.loser_rating_before}`⮕`{game.loser_rating_after}[{game.loser_income}]`\n"

        players_text = f"{description if description else 'Пусто.'}"
        embed.description = f"{players_text}"
        await ctx.respond(embed=embed, ephemeral=True)

    @player.command(description="Пригласить игрока в сессию.")
    @is_user_in_db()
    async def rank(self, ctx: ApplicationContext):
        async with PlayerService(ctx.user.id, ctx=ctx) as service:
            players, start_rank = await service.get_my_position()
            enumerated_players = enumerate(players, start=start_rank)
            embed = discord.Embed(title=f"Позиция в рейтинге", color=discord.Color.dark_grey())
            players_text = "\n".join(
                f"`{str(index).rjust(2, ' ')}. {str(player.rating).rjust(4, ' ')}` <@{player.id}>"
                for index, player in enumerated_players
            )
            players_text = f"\n{players_text if players_text else 'Пусто.'}"
            embed.description = f"{players_text}"
            await ctx.respond(embed=embed, ephemeral=True)

    @player.command(description="Посмотреть свое место в рейтинговой таблице.")
    @cooldown(1, settings.INVITE_COOLDOWN, commands.BucketType.user)
    @is_user_in_db()
    async def invite(self, ctx: ApplicationContext, player: discord.Member):
        await ctx.defer(ephemeral=True)

        async with PlayerService(player.id, ctx=ctx) as service:
            player_ = await service.get_instance()
            if not player_:
                raise PlayerNotCreatedError()
            elif not player_.in_search:
                raise PlayerNotInSearchError()
            elif player.id == ctx.user.id:
                raise PlayerSelfInviteError()

        await ctx.respond(f"Ожидаем ответа от {player.mention}.", ephemeral=True)
        confirm_view = Confirm(initiator=ctx.user.id, invited=player.id)

        if player.can_send():
            private = await player.send(f"{ctx.user.mention} приглашает {player.mention} в сессию.", view=confirm_view)
            await confirm_view.wait()
            await private.edit(view=confirm_view)

            if confirm_view.value:
                msg = f"{player.mention} принял приглашение."
                category = discord.utils.get(ctx.guild.categories, id=settings.CATEGORY_FOR_VOICES_ID)

                if not category:
                    msg = "Категория для сессии не найдена."
                    await ctx.respond(msg, delete_after=settings.DELETE_AFTER, ephemeral=True)
                else:
                    overwrites = {
                        ctx.guild.default_role: discord.PermissionOverwrite(connect=False),
                        ctx.user: discord.PermissionOverwrite(connect=True),
                        player: discord.PermissionOverwrite(connect=True),
                    }
                    voice_title = "{} vs {}".format(ctx.user.display_name, player.display_name)
                    voice = await category.create_voice_channel(name=voice_title, overwrites=overwrites)
                    buttons = ResultsButtons(initiator_id=ctx.user.id, invited_id=player.id)

                    await voice.send(view=buttons)

                    map_ = random.choice(list(Map))
                    await player.send(f"Приглашение в сессию от {ctx.user.mention}. Карта: {map_}.\n{voice.jump_url}")
                    await ctx.user.send(f"Приглашение в сессию. Карта: {map_}.\n{voice.jump_url}")

            elif confirm_view.value is None:
                msg = f"{player.mention} не ответил на приглашение."
            else:
                msg = f"{player.mention} отклонил приглашение."

            async with PlayerService(ctx.user.id, ctx=ctx) as service:
                async with service.session.begin():
                    await service.update(in_search=False)

            async with PlayerService(player.id, ctx=ctx) as service:
                async with service.session.begin():
                    await service.update(in_search=False)

            await ctx.respond(msg, delete_after=settings.DELETE_AFTER, ephemeral=True)
            await ctx.delete()
        else:
            await ctx.respond(f"{player.mention} не может получать личные сообщения.", ephemeral=True)

    async def cog_check(self, ctx: ApplicationContext):
        """Проверка на наличие ролей соответствия для всего модуля игроков."""

        if not all(roles_ids.values()):
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
        elif isinstance(error, (PlayerNotInSearchError, PlayerSelfInviteError, PlayerAlreadyCreatedError)):
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
            raise error
