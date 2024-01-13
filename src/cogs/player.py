import discord
from discord import Cog, ApplicationContext, SlashCommandGroup
from discord.ext.commands import Bot

from src import texts, database
from src.checks import is_user_in_db
from src.config import settings
from src.errors.player import NotSetRolesError, PlayerNotCreatedError
from src.models import Player
from src.services.roles import RolesService


class PlayerCog(Cog, guild_ids=[settings.GUILD_ID]):
    def __init__(self, bot: Bot):
        self.bot = bot

    player = SlashCommandGroup("player", "Группа команд для игроков.")

    async def cog_check(self, ctx: ApplicationContext):
        """Проверка на наличие ролей соответствия для всего модуля игроков."""

        # if not all(database.roles.values()):
        #     raise NotSetRolesError()

        return True

    async def cog_command_error(self, ctx: ApplicationContext, error: Exception) -> None:
        """Обработка ошибок для модуля игроков."""
        if isinstance(error, NotSetRolesError):
            admin_cog = self.bot.get_cog("AdminCog")
            admin_commands = discord.utils.get(admin_cog.get_commands(), name="admin")
            set_roles = discord.utils.get(admin_commands.walk_commands(), name="set_roles")  # noqa
            await ctx.respond(f"{str(error)}\n{set_roles.mention}.")
        elif isinstance(error, PlayerNotCreatedError):
            player_commands = discord.utils.get(self.get_commands(), name="player")
            start = discord.utils.get(player_commands.walk_commands(), name="start")  # noqa
            await ctx.respond(f"{str(error)} Регистрация в боте: {start.mention}.")
        else:
            print(error)
            await ctx.respond(f"Модуль игроков: {texts.errors['unknown']}")

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

        await ctx.respond("Игрок создан.", embed=player.embed, delete_after=30, ephemeral=True)

    @player.command(description="Начать поиск игры.")
    @is_user_in_db()
    async def go(self, ctx: ApplicationContext):
        await ctx.defer()

        player = database.players[ctx.user.id]
        player.in_search = True
        await ctx.respond("Поиск начат.", embed=player.embed, delete_after=30, ephemeral=True)
