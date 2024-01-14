import discord
from discord import Cog, ApplicationContext, SlashCommandGroup, Interaction
from discord.ext import commands
from discord.ext.commands import Bot, Cooldown, CooldownMapping, cooldown

from src import texts, database
from src.checks import is_user_in_db
from src.config import settings
from src.errors.player import NotSetRolesError, PlayerNotCreatedError
from src.models import Player
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

    @player.command(description="Пригласить игрока в сессию.")
    @cooldown(1, settings.COOLDOWN_INVITE, commands.BucketType.user)
    @is_user_in_db()
    async def invite(self, ctx: ApplicationContext, player: discord.Member):
        await ctx.defer()
        await ctx.respond(f"Ожидаем ответа от {player.mention}.", delete_after=settings.DELETE_AFTER, ephemeral=True)

        if player.id not in database.players:
            raise PlayerNotCreatedError()
        elif player.id == ctx.user.id:
            await ctx.respond("Нельзя пригласить самого себя.", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return

        view = Confirm(initiator=ctx.user.id, invited=player.id)
        try:
            private_message = await player.send(f"{ctx.user.mention} приглашает {player.mention} в сессию.", view=view)
            await view.wait()
            await private_message.edit(view=view)
        except discord.errors.Forbidden:
            await ctx.respond(
                f"{player.mention} не принимает личные сообщения.", delete_after=settings.DELETE_AFTER, ephemeral=True
            )
            return
        except discord.errors.HTTPException:
            await ctx.respond(f"Ошибка при отправке приглашения.", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        else:
            # TODO Логика ожидания записьвать в бд
            # initiator, invited = database.players[ctx.user.id], database.players[player.id]
            if view.value is None:
                msg = f"{player.mention} не ответил на приглашение."
            elif view.value:
                msg = f"{player.mention} принял приглашение."
            else:
                msg = f"{player.mention} отклонил приглашение."

            await ctx.respond(msg, delete_after=settings.DELETE_AFTER, ephemeral=True)

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
