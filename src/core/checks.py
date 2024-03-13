from discord.ext.commands import check
from sqlalchemy import exists, select

from src.core.database import async_session_maker
from src.core.models import Player
from src.errors.player import PlayerNotCreatedError


def is_user_in_db():
    """Проверка на наличие игрока в базе данных."""

    async def predicate(ctx):
        async with async_session_maker() as session:
            stmt = exists().where(Player.id == ctx.user.id)
            result = await session.execute(select(stmt))
            if result.scalar():
                return True

        raise PlayerNotCreatedError()

    return check(predicate)  # noqa
