from src.models import Player, Rank

players: dict[int, Player] = {
    412350766662156289: Player(id=412350766662156289, in_search=True, rating=100),
}
roles = {
    Rank.neofit: 1195819868247830580,
    Rank.adept: 1195819965304012833,
    Rank.master: 1195820003514134579,
    Rank.archon: None,
    Rank.ethereal: None,
    Rank.officer: None,
}

session_channel = 1196106456974504096
session_messages = {rank: None for rank in Rank.list()}

# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy import text
#
# Base = declarative_base()
#
# class AsyncDatabase:
#     def __init__(self, db_url):
#         self.engine = create_async_engine(db_url)
#         self.session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
#
#     async def __aenter__(self):
#         self._session = self.session()
#         return self._session
#
#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         if exc_type is not None:
#             await self._session.rollback()
#         await self._session.close()
#
#     async def execute(self, query, **kwargs):
#         async with self as session:
#             result = await session.execute(text(query), kwargs)
#             await session.commit()
#             return result
#
#     async def add(self, instance):
#         async with self as session:
#             session.add(instance)
#             await session.commit()
