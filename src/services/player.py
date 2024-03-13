from discord import EmbedField, Embed
from sqlalchemy import select, func

from src.core.config import settings
from src.core.enum import Rank
from src.core.models import Player, Game
from src.core.utils import get_rank_by_rating, get_rating_min_max_by_rank
from src.services._abs import Service


class PlayerService(Service):
    model = Player

    async def get_my_last_10_games(self):
        return (
            await self.session.scalars(
                select(Game)
                .filter((Game.winner_id == self.entity_id) | (Game.loser_id == self.entity_id))
                .filter(Game.is_active == True)
                .order_by(Game.id.desc())
                .limit(10)
            )
        ).all()

    async def get_my_position(self):
        total_players = await self.session.scalar(select(func.count()).select_from(Player))

        subquery = (
            select(Player.id, Player.rating, func.rank().over(order_by=Player.rating.desc()).label("rank"))
            .order_by(Player.rating.desc())
            .subquery()
        )

        query = select(subquery.c.rank).where(subquery.c.id == self.entity_id)
        player_rank = await self.session.scalar(query)

        if total_players > 10:
            start_rank = max(1, player_rank - 5)
            end_rank = min(total_players, player_rank + 5)
        else:
            start_rank = 1
            end_rank = total_players

        stmt = (
            select(subquery.c.id, subquery.c.rating)
            .where(subquery.c.rank.between(start_rank, end_rank))
            .order_by(subquery.c.rank)
        )
        players = await self.session.execute(stmt)
        return players, start_rank

    async def get_leaderboard_players(self, count_players: int = settings.LEADERBOARD_COUNT):
        stmt = select(self.model).order_by(self.model.rating.desc()).limit(count_players)
        result = await self.session.scalars(stmt)
        return result

    async def rate(self, winner_id: int, loser_id: int) -> None:
        winner: Player = await self.get(self.model.id == winner_id)
        loser: Player = await self.get(self.model.id == loser_id)

        winner_rating_before = winner.rating
        loser_rating_before = loser.rating

        winner_rank = get_rank_by_rating(winner.rating)
        loser_rank = get_rank_by_rating(loser.rating)

        delta = winner_income = loser_income = (
            Rank.difference(loser_rank, winner_rank) * settings.RATING_DELTA + settings.RATING_DEFAULT_MOVEMENT
        )

        new_rating__loser = loser.rating - delta

        if new_rating__loser < 0:
            loser.rating = 0
            loser_income = loser.rating
        else:
            loser.rating = new_rating__loser

        winner.rating += delta

        self.session.add(
            Game(
                winner_id=winner_id,
                winner_rating_before=winner_rating_before,
                winner_income=winner_income,
                winner_rating_after=winner.rating,
                loser_id=loser_id,
                loser_rating_before=loser_rating_before,
                loser_income=loser_income,
                loser_rating_after=loser.rating,
            )
        )

    async def get_player_embed(self):
        rank = get_rank_by_rating(self.instance.rating)
        return Embed(
            fields=[
                EmbedField(name="", value=f"<@{self.entity_id}>", inline=False),
                EmbedField(name="В поиске", value="Да" if self.instance.in_search else "Нет"),
                EmbedField(name="Рейтинг", value=str(self.instance.rating)),
                EmbedField(name="Ранг", value=rank),
            ]
        )

    async def get__in_search__players(self, rank: Rank):
        min_rating, max_rating = get_rating_min_max_by_rank(rank)
        stmt = select(self.model).where(
            Player.in_search == True,
            Player.rating >= min_rating,
            Player.rating < max_rating,
        )
        result = await self.session.scalars(stmt)
        players = result.all()
        return players
