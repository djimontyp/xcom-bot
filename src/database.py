from collections import defaultdict

from src.models import Player, Rank

players: dict[int, Player] = {}
roles = {
    "neofit": 1195819868247830580,
    "adept": 1195819965304012833,
    "master": 1195820003514134579,
    # "neofit": None,
    # "adept": None,
    # "master": None,
}

session_channel = None
session_messages = {rank: None for rank in Rank.list()}
