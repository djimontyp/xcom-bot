import discord
from discord import (
    Cog,
    ApplicationContext,
    SlashCommandGroup,
    Embed,
)
from discord.ext import tasks
from discord.ext.commands import Bot

from src.components.options import RanksAutocomplete
from src.core import database, utils
from src.core.config import settings
from src.core.enum import Rank
from src.core.models import Player
from src.core.utils import role_mention, get_rank_by_rating
from src.services.player import PlayerService


class AdminCog(Cog, guild_ids=[settings.GUILD_ID]):
    def __init__(self, bot: Bot):
        self.invite = None
        self.bot = bot
        self.refresh_session_messages.start()
        self.leaderboard.start()

    admin = SlashCommandGroup("admin", "Группа команд для администраторов.", hidden=True)

    @admin.command(description="Показать установленные роли соответствия для рангов.", hidden=True)
    async def roles(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)

        embed = Embed(title="Роли")
        embed.add_field(name=Rank.neofit, value=role_mention(Rank.neofit))
        embed.add_field(name=Rank.adept, value=role_mention(Rank.adept))
        embed.add_field(name=Rank.officer, value=role_mention(Rank.officer))
        embed.add_field(name=Rank.master, value=role_mention(Rank.master))
        embed.add_field(name=Rank.archon, value=role_mention(Rank.archon))
        embed.add_field(name=Rank.ethereal, value=role_mention(Rank.ethereal))

        await ctx.respond(embed=embed, delete_after=settings.DELETE_AFTER, ephemeral=True)

    @admin.command(description="Вызвать сообщение для поиска сессии с авто обновлением для ранга.", hidden=True)
    async def session_message(self, ctx: ApplicationContext, rank: RanksAutocomplete):
        await ctx.defer(ephemeral=True)

        message = await ctx.channel.send(f"Сообщение для ранга {rank}")
        database.session_messages.update({rank: message.id})

        await ctx.delete()

    @tasks.loop(seconds=settings.LEADERBOARD_REFRESH_TIME)
    async def leaderboard(self):
        channel = self.bot.get_channel(settings.SESSION_CHANNEL)
        message = await channel.fetch_message(settings.LEADERBOARD_MESSAGE)

        async with PlayerService() as service:
            players: list[Player] = await service.get_leaderboard_players()

        enumerated_players = enumerate(players, 1)

        embed = discord.Embed(title=f"Топ {settings.LEADERBOARD_COUNT} Чемпионов", color=discord.Color.dark_gold())
        embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url)

        players_text = "\n".join(
            f"`{str(index).rjust(2, ' ')}. {get_rank_by_rating(player.rating).ljust(7, ' ')} {str(player.rating).rjust(4, ' ')}` <@{player.id}>"
            for index, player in enumerated_players
        )
        players_text = f"\n{players_text if players_text else 'Никого нет.'}"
        embed.description = f"{players_text}"
        await message.edit(content="", embed=embed)

    @tasks.loop(seconds=settings.REFRESH_TIME)
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
                    if not (channel := self.bot.get_channel(settings.SESSION_CHANNEL)):
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
                    async with PlayerService() as service:
                        players = await service.get__in_search__players(rank)

                    enumerated_players = enumerate(players, 1)
                    # icons = {
                    #     Rank.neofit: "123",
                    #     Rank.adept: "123"
                    # }
                    # {icons[utils.get_rank_by_rating(player.rating)]}
                    #
                    # для заменьі 💪
                    players_text = "\n".join(
                        f"{index}. 💪 **`{str(player.rating).rjust(4, ' ')}`**<@{player.id}>"
                        for index, player in enumerated_players
                    )
                    players_text = f"**{rank.value}**\n{players_text if players_text else '∞'}"
                    msg = f"{players_text}\nㅤ"
                    await message.edit(content=msg)

    @refresh_session_messages.before_loop
    async def before_refresh_session_messages(self):
        await self.bot.wait_until_ready()

    @leaderboard.before_loop
    async def before_refresh_leaderboard(self):
        await self.bot.wait_until_ready()
