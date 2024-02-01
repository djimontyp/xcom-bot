from src.core.config import settings
from src.core.enum import Rank


def get_rank_by_rating(rating: int) -> Rank | None:
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


roles_ids__mapper = {
    Rank.neofit: settings.ROLE_NEOFIT,
    Rank.adept: settings.ROLE_ADEPT,
    Rank.master: settings.ROLE_MASTER,
    Rank.officer: settings.ROLE_OFFICER,
    Rank.archon: settings.ROLE_ARCHON,
    Rank.ethereal: settings.ROLE_ETHEREAL,
}
