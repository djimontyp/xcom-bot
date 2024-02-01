from discord.ext.commands import check

from src.core import database
from src.errors.player import PlayerNotCreatedError


def is_user_in_db():
    """Проверка на наличие игрока в базе данных."""

    async def predicate(ctx):
        if ctx.user.id in database.players:
            return True
        raise PlayerNotCreatedError()

    return check(predicate)  # noqa
