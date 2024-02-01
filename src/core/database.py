from datetime import datetime

from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declared_attr

from src.core.config import settings
from src.core.models import Player
from src.core.enum import Rank

engine = create_async_engine(settings.DB_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
    }

    @declared_attr
    def __tablename__(cls) -> str:  # noqa
        return cls.__name__.lower()


players: dict[int, Player] = {
    412350766662156289: Player(id=412350766662156289, in_search=True, rating=100),
    1128775596781088798: Player(id=1128775596781088798, in_search=True, rating=100),
}

session_messages = {rank: None for rank in list(Rank)}
