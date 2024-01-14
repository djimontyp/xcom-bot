from discord import AutocompleteContext, OptionChoice, Option
from discord.utils import basic_autocomplete

from src.models import Rank


async def ranks_options(ctx: AutocompleteContext):
    return [OptionChoice(name=rank, value=rank) for rank in Rank.list()]


RanksAutocomplete = Option(
    str,
    name="rank",
    description="Ранг для которого будет создано и обновляться сообщение.",
    autocomplete=basic_autocomplete(ranks_options),
)
