# Discord привилегии.

import discord
from discord.ext.commands import Bot
from discord.ext.prettyhelp import PrettyHelp

from src.cogs.admin import AdminCog
from src.cogs.player import PlayerCog
from src.core.config import settings

intents = discord.Intents.all()
intents.members = True  # noqa
intents.message_content = True  # noqa
xcom_bot = Bot(command_prefix="/", intents=intents)

xcom_bot.add_cog(PlayerCog(xcom_bot))
xcom_bot.add_cog(AdminCog(xcom_bot))

xcom_bot.help_command = PrettyHelp()


@xcom_bot.event
async def on_message(message):
    # Проверяем, что сообщение отправлено не ботом
    if message.author.bot:
        return

    # Проверяем, что сообщение отправлено в определенный канал
    if message.channel.id == settings.SESSION_CHANNEL:
        await message.delete()


if __name__ == "__main__":
    xcom_bot.run(settings.DISCORD_BOT_TOKEN)
