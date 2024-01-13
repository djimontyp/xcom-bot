# Discord привилегии.
import typing

import discord
from discord.ext.commands import Bot

from src.cogs.admin import AdminCog
from src.cogs.player import PlayerCog
from src.config import settings

if typing.TYPE_CHECKING:
    pass

intents = discord.Intents.all()
intents.members = True  # noqa
intents.message_content = True  # noqa
xcom_bot = Bot(command_prefix="/", intents=intents)

xcom_bot.add_cog(PlayerCog(xcom_bot))
xcom_bot.add_cog(AdminCog(xcom_bot))

if __name__ == "__main__":
    xcom_bot.run(settings.DISCORD_BOT_TOKEN)
