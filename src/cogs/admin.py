import discord
from discord import (
    Cog,
    ApplicationContext,
    SlashCommandGroup,
    Role,
    TextChannel,
    Option,
)
from discord.ext import tasks
from discord.ext.commands import Bot

from src import database
from src.config import settings
from src.options import ranks_options, RanksAutocomplete
from src.services.roles import RolesService


class AdminCog(Cog, guild_ids=[settings.GUILD_ID]):
    def __init__(self, bot: Bot):
        self.invite = None
        self.bot = bot
        self.refresh_session_messages.start()

    admin = SlashCommandGroup("admin", "Группа команд для администраторов.")

    @admin.command(description="Установить роли соответствия для рангов.")
    async def set_roles(
        self,
        ctx: ApplicationContext,
        neofit: Role | None,
        adept: Role | None,
        master: Role | None,
        archon: Role | None,
        ethereal: Role | None,
        officer: Role | None,
    ):
        await ctx.defer()

        roles = RolesService()
        roles.update(neofit=neofit.id) if neofit else ...
        roles.update(adept=adept.id) if adept else ...
        roles.update(master=master.id) if master else ...
        roles.update(archon=archon.id) if archon else ...
        roles.update(ethereal=ethereal.id) if ethereal else ...
        roles.update(officer=officer.id) if officer else ...

        await ctx.respond(embed=roles.get_embed("Роли обновлены."), delete_after=settings.DELETE_AFTER, ephemeral=True)

    @admin.command(description="Установить канал для поиска сессии.")
    async def set_session_channel(self, ctx: ApplicationContext, channel: TextChannel):
        await ctx.defer()
        database.session_channel = channel.id
        await ctx.respond(
            f"Канал для поиска сессии установлен на {channel.mention}.",
            delete_after=settings.DELETE_AFTER,
            ephemeral=True,
        )

    @admin.command(description="Показать канал для поиска сессии.")
    async def session_channel(self, ctx: ApplicationContext):
        await ctx.defer()

        if channel := ctx.guild.get_channel(database.session_channel):
            await ctx.respond(
                f"Канал поиска сессии: {channel.mention}.", delete_after=settings.DELETE_AFTER, ephemeral=True
            )
        else:
            await ctx.respond(f"Канал поиска сессии не найден.", delete_after=settings.DELETE_AFTER, ephemeral=True)

    @admin.command(description="Показать установленные роли соответствия для рангов.")
    async def roles(self, ctx: ApplicationContext):
        await ctx.defer()
        embed = RolesService().get_embed()
        await ctx.respond(embed=embed, delete_after=settings.DELETE_AFTER, ephemeral=True)

    @admin.command(description="Вызвать сообщение для поиска сессии с авто обновлением для ранга.")
    async def session_message(self, ctx: ApplicationContext, rank: RanksAutocomplete):
        await ctx.defer()

        message = await ctx.channel.send(f"Сообщение для ранга {rank}")
        database.session_messages.update({rank: message.id})

        await ctx.delete()

    @tasks.loop(seconds=settings.REFRESH_SESSION_MESSAGES_INTERVAL)
    async def refresh_session_messages(self):
        """Обновление сообщений с ролями для поиска сессии.

        !!! Возможно не самое лучшее решение, но пока что так.
        Если будет много игроков то возможна ошибка превышения лимита символов в сообщении.
        """
        if not self.invite:
            player_cog = self.bot.get_cog("PlayerCog")
            player_commands = discord.utils.get(player_cog.get_commands(), name="player")
            self.invite = discord.utils.get(player_commands.walk_commands(), name="invite")  # noqa

        for rank, message_id in database.session_messages.items():
            if message_id:
                try:
                    if not (channel := self.bot.get_channel(database.session_channel)):
                        continue
                    message = await channel.fetch_message(message_id)
                except discord.NotFound:
                    database.session_messages.update({rank: None})
                    continue
                except discord.Forbidden:
                    continue
                except discord.HTTPException:
                    continue
                else:
                    players = {
                        player.id: player
                        for player in database.players.values()
                        if player.in_search and player.rank == rank
                    }
                    enumerated_players = enumerate(players.values(), 1)
                    invite = f"Пригласить в игру: {self.invite.mention}\n\n"
                    players_text = "\n".join(
                        f"{index}. **`{player.rank}[{player.rating}]`** — {player.mention}"
                        for index, player in enumerated_players
                    )
                    players_text = players_text or "Никого нет."
                    msg = invite + players_text
                    await message.edit(content=msg)

    @refresh_session_messages.before_loop
    async def before_refresh_session_messages(self):
        await self.bot.wait_until_ready()
