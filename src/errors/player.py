from discord import CheckFailure


class NotSetRolesError(CheckFailure):
    """Ошибка, если не установлены роли соответствия для рангов."""

    def __init__(self, text: str = "Роли не установлены. Обратитесь к администратору для настройки бота."):
        super().__init__(text)


class PlayerNotCreatedError(CheckFailure):
    """Ошибка, если не создан игрок."""

    def __init__(self, text: str = "Игрок не создан."):
        super().__init__(text)


class PlayerAlreadyCreatedError(CheckFailure):
    """Ошибка, если игрок уже создан."""

    def __init__(self, player, text: str = "Игрок уже создан."):
        self.player = player
        super().__init__(text)


class PlayerNotInSearchError(CheckFailure):
    """Ошибка, если игрок не в поиске игры."""

    def __init__(self, text: str = "Игрок не в режиме поиска игры."):
        super().__init__(text)


class NotAllowedToInteractError(CheckFailure):
    """Ошибка, если игрок не может взаимодействовать с сессией."""

    def __init__(self, text: str = "Вы не можете взаимодействовать с сессией."):
        super().__init__(text)


class PlayerSelfInviteError(CheckFailure):
    """Ошибка, если игрок сам себя пригласил."""

    def __init__(self, text: str = "Вы не можете пригласить самого себя."):
        super().__init__(text)
