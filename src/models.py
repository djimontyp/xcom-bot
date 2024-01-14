from dataclasses import dataclass
from enum import StrEnum
from functools import cached_property
from typing import Optional

from discord import Embed
from pydantic import BaseModel, Field

from src.config import settings


class Player(BaseModel):
    id: int = Field(..., description="Discord идентификатор игрока.")
    in_search: bool = Field(False, description="Игрок в поиске игры.")
    rating: Optional[int] = Field(settings.INITIAL_RATING, description="Рейтинг игрока.")

    @property
    def embed(self):
        embed = Embed()
        embed.add_field(name="", value=self.mention, inline=False)
        embed.add_field(name="В поиске", value="Да" if self.in_search else "Нет")
        embed.add_field(name="Рейтинг", value=str(self.rating))
        return embed

    @cached_property
    def mention(self):
        return f"<@{self.id}>"

    @property
    def rank(self):
        rating = self.rating
        if 0 <= rating < 199:
            return Rank.neofit
        elif 200 <= rating < 499:
            return Rank.adept
        elif 500 <= rating < 999:
            return Rank.officer
        elif 1000 <= rating < 1499:
            return Rank.master
        elif 1500 <= rating < 1999:
            return Rank.archon
        elif 2000 <= rating:
            return Rank.ethereal
        else:
            return "Not found"


class Rank(StrEnum):
    neofit = "Неофит"
    adept = "Адепт"
    officer = "Офицер"
    master = "Мастер"
    archon = "Архонт"
    ethereal = "Эфирниал"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
