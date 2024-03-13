from src.core.config import settings
from src.core.enum import Rank


def get_rank_by_rating(rating: int) -> Rank | None:
    if rating < 1200:
        return Rank.neofit
    elif 1200 <= rating < 1500:
        return Rank.adept
    elif 1500 <= rating < 2000:
        return Rank.officer
    elif 2000 <= rating < 2500:
        return Rank.master
    elif 2500 <= rating < 3000:
        return Rank.archon
    elif 3000 <= rating:
        return Rank.ethereal
    else:
        return Rank.neofit


def get_rating_min_max_by_rank(rank: Rank):
    if rank == Rank.neofit:
        return 0, 1200
    elif rank == Rank.adept:
        return 1200, 1500
    elif rank == Rank.officer:
        return 1500, 2000
    elif rank == Rank.master:
        return 2000, 2500
    elif rank == Rank.archon:
        return 2500, 3000
    elif rank == Rank.ethereal:
        return 3000, float("inf")


roles_ids = {
    Rank.neofit: settings.ROLE_NEOFIT,
    Rank.adept: settings.ROLE_ADEPT,
    Rank.master: settings.ROLE_MASTER,
    Rank.officer: settings.ROLE_OFFICER,
    Rank.archon: settings.ROLE_ARCHON,
    Rank.ethereal: settings.ROLE_ETHEREAL,
}


def role_mention(rank: Rank):
    return f"<@&{roles_ids[rank]}>"
