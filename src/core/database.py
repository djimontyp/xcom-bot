from datetime import datetime
from uuid import uuid4

from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declared_attr

from src.core.config import settings
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


session_messages = {
    Rank.neofit: settings.SEARCH_MESSAGE__NEOFIT,
    Rank.adept: settings.SEARCH_MESSAGE__ADEPT,
    Rank.officer: settings.SEARCH_MESSAGE__OFFICER,
    Rank.master: settings.SEARCH_MESSAGE__MASTER,
    Rank.archon: settings.SEARCH_MESSAGE__ARCHON,
    Rank.ethereal: settings.SEARCH_MESSAGE__ETHEREAL,
}
