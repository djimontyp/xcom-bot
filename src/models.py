from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from discord import Embed
from pydantic import BaseModel, Field

from src.config import settings


class Player(BaseModel):
    id: int = Field(..., description="Discord идентификатор игрока.")
    in_search: bool = Field(False, description="Игрок в поиске игры.")
    rating: Optional[int] = Field(settings.INITIAL_RATING, description="Рейтинг игрока.")

    @cached_property
    def mention(self):
        return f"<@{self.id}>"

    @property
    def embed(self):
        embed = Embed()
        embed.add_field(name="", value=self.mention, inline=False)
        embed.add_field(name="В поиске", value="Да" if self.in_search else "Нет")
        embed.add_field(name="Рейтинг", value=str(self.rating))
        return embed
