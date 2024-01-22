from src import database
from src.config import settings
from src.models import Rank


class Rating:
    def __init__(self, winner_id: int, loser_id: int, /):
        self.winner = database.players[winner_id]
        self.loser = database.players[loser_id]
        self.delta = (
            Rank.difference(self.winner.rank, self.loser.rank) * settings.RATING_DELTA
            + settings.RATING_DEFAULT_MOVEMENT
        )

    def rate(self) -> None:
        winner, loser, delta = self.winner, self.loser, self.delta

        if (loser.rating - delta) < 0:
            loser.rating = 0
        else:
            loser.rating -= delta

        winner.rating += delta
