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

    id: Mapped[int] = mapped_column(primary_key=True, doc="Discord идентификатор игрока.")
    in_search: Mapped[bool] = mapped_column(default=False, doc="Игрок в поиске игры.")
    rating: Mapped[int] = mapped_column(default=settings.INITIAL_RATING, doc="Рейтинг игрока.")
