from discord import EmbedField, Embed

from src.core import database
from src.core.config import settings
from src.core.enum import Rank
from src.core.utils import get_rank_by_rating
from src.core.models import Player
from src.services._abs import Service


class PlayerService(Service):
    model = Player

    @staticmethod
    def rate(winner_id: int, loser_id: int) -> None:
        winner = database.players[winner_id]
        loser = database.players[loser_id]
        winner_rank = get_rank_by_rating(winner.rating)
        loser_rank = get_rank_by_rating(loser.rating)
        delta = Rank.difference(winner_rank, loser_rank) * settings.RATING_DELTA + settings.RATING_DEFAULT_MOVEMENT

        if (loser.rating - delta) < 0:
            loser.rating = 0
        else:
            loser.rating -= delta

        winner.rating += delta

    async def get_player_embed(self):
        return Embed(
            fields=[
                EmbedField(name="", value=self.instance.mention, inline=False),
                EmbedField(name="В поиске", value="Да" if self.instance.in_search else "Нет"),
                EmbedField(name="Рейтинг", value=str(self.instance.rating)),
                EmbedField(name="Ранг", value=self.instance.rank),
            ]
        )
