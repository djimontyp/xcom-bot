from sqlalchemy import SmallInteger, BigInteger
from sqlalchemy.orm import mapped_column, Mapped

from src.core.config import settings
from src.core.database import Base


class Player(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = None

    @property
    def service(self):
        return self._service

    @service.setter
    def service(self, value):
        value.player = self
        self._service = value

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, doc="Discord идентификатор игрока.")
    in_search: Mapped[bool] = mapped_column(default=False, doc="Игрок в поиске игры.")
    rating: Mapped[int] = mapped_column(SmallInteger(), default=settings.INITIAL_RATING, doc="Рейтинг игрока.")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, rating={self.rating}>"


class Game(Base):
    id: Mapped[int] = mapped_column(primary_key=True)

    winner_id: Mapped[int] = mapped_column(BigInteger())
    winner_rating_before: Mapped[int] = mapped_column(SmallInteger())
    winner_income: Mapped[int] = mapped_column(SmallInteger())
    winner_rating_after: Mapped[int] = mapped_column(SmallInteger())

    loser_id: Mapped[int] = mapped_column(BigInteger())
    loser_rating_before: Mapped[int] = mapped_column(SmallInteger())
    loser_income: Mapped[int] = mapped_column(SmallInteger())
    loser_rating_after: Mapped[int] = mapped_column(SmallInteger())

    is_active: Mapped[bool] = mapped_column(
        default=True, doc="Для исключения игр. Аналог удаления, но без фактического удаления."
    )
