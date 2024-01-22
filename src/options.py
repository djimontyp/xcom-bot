from discord import Option
from discord.utils import basic_autocomplete

from src.models import Rank

RanksAutocomplete = Option(
    str,
    name="rank",
    description="Ранг для которого будет создано и обновляться сообщение.",
    autocomplete=basic_autocomplete(list(Rank)),
)
