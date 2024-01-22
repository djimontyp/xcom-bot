import random

import discord
from discord import Cog, ApplicationContext, SlashCommandGroup, Interaction
from discord.ext import commands
from discord.ext.commands import Bot, cooldown
from discord.ui import Item

from src import texts, database
from src.checks import is_user_in_db
from src.config import settings
from src.errors.player import NotSetRolesError, PlayerNotCreatedError, PlayerNotInSearchError, PlayerSelfInviteError
from src.models import Player, Map, GameResult
from src.services.roles import RolesService


class Confirm(discord.ui.View):
    def __init__(self, initiator: int, invited: int):
        super().__init__()
        self.value = None
        self.initiator = initiator
        self.invited = invited

    @discord.ui.button(label="Подтвердить", style=discord.ButtonStyle.green)
    async def confirm_callback(self, button: discord.ui.Button, interaction: Interaction):
        self.disable_all_items()
        await interaction.response.send_message("Подтверждено", ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_callback(self, button: discord.ui.Button, interaction: Interaction):
        self.disable_all_items()
        await interaction.response.send_message("Отменено", ephemeral=True)
        self.value = False
        self.stop()

    async def on_timeout(self) -> None:
        self.disable_all_items()


class ResultsButtons(discord.ui.View):
    def __init__(self, initiator: int, invited: int):
        super().__init__()
        self.initiator = initiator
        self.invited = invited

        self.result: dict[int, GameResult | None] = {
            initiator: None,
            invited: None,
        }

    @discord.ui.button(label="Победа", style=discord.ButtonStyle.green, custom_id="win_callback")
    async def win_callback(self, button: discord.ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.result[interaction.user.id] = GameResult.win
        await self.update_buttons_labels(interaction)

    @discord.ui.button(label="Поражение", style=discord.ButtonStyle.red, custom_id="lose_callback")
    async def lose_callback(self, button: discord.ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.result[interaction.user.id] = GameResult.lose
        await self.update_buttons_labels(interaction)

    @discord.ui.button(label="Ничья", style=discord.ButtonStyle.grey, custom_id="draw_callback")
    async def draw_callback(self, button: discord.ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.result[interaction.user.id] = GameResult.draw
        await self.update_buttons_labels(interaction)

    async def update_buttons_labels(self, interaction: Interaction):
        initiator, invited = database.players[self.initiator], database.players[self.invited]
        initiator_result, invited_result = self.result[self.initiator], self.result[self.invited]

        if initiator_result and invited_result:
            match initiator_result, invited_result:
                case GameResult.win, GameResult.lose:
                    initiator.rating += 10
                    invited.rating -= 10
                case GameResult.lose, GameResult.win:
                    initiator.rating -= 10
                    invited.rating += 10
                case GameResult.draw:
                    ...
                case _:
                    raise ValueError(f"Парадоксальная комбинация: {initiator_result}, {invited_result}")
            await interaction.response.edit_message(
                content=f"Результаты сессии: {initiator_result} vs {invited_result}",
                view=None,
            )
        await interaction.channel.send(
            f"Обновлены результаты сессии: {initiator.mention}{initiator_result} vs {invited.mention} [{invited_result}]",
        )

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id not in self.result:
            raise discord.errors.CheckFailure()
        return True

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        if isinstance(error, discord.errors.CheckFailure):
            await interaction.response.send_message("Вы не участвуете в сессии.", ephemeral=True)


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
        if not (neofit := roles_service.get_role(ctx, "neofit")):
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
    @cooldown(1, settings.COOLDOWN_INVITE, commands.BucketType.user)
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

                    buttons = ResultsButtons(initiator=ctx.user.id, invited=player.id)
                    await voice.send(view=buttons)

                    database.players[ctx.user.id].in_search, database.players[player.id].in_search = False, False

                    map_ = random.choice(Map.list())
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

        if not all(database.roles.values()):
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
                f"Модуль игроков: {texts.errors['unknown']}",
                ephemeral=True,
                delete_after=settings.DELETE_AFTER,
            )
