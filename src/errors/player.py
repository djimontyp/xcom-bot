from discord import CheckFailure


class NotSetRolesError(CheckFailure):
    """Ошибка, если не установлены роли соответствия для рангов."""

    def __init__(self, text: str = "Роли не установлены. Обратитесь к администратору для настройки бота."):
        super().__init__(text)


class PlayerNotCreatedError(CheckFailure):
    """Ошибка, если не создан игрок."""

    def __init__(self, text: str = "Игрок не создан."):
        super().__init__(text)
