from enum import StrEnum


class Rank(StrEnum):
    neofit = "Неофит"
    adept = "Адепт"
    officer = "Офицер"
    master = "Мастер"
    archon = "Архонт"
    ethereal = "Эфирниал"

    @classmethod
    def difference(cls, rank1, rank2):
        ranks = list(cls)
        return ranks.index(rank1) - ranks.index(rank2)

    @property
    def mention(self):
        return f"<@&{self.value}>"


class Map(StrEnum):
    abductor = "Abductor"
    battleship = "Battleship"
    cargo = "Cargo"
    council = "Council"
    exalt = "Exalt"
    exalt_base = "Exalt Base"
    exalt_hq = "Exalt HQ"
    exalt_prison = "Exalt Prison"


class GameResult(StrEnum):
    win = "Победа"
    lose = "Поражение"
    draw = "Ничья"
