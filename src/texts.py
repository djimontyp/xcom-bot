import string

player = {
    "added": string.Template("Игрок ${player} добавлен в базу данных. Начальный рейтинг: ${rating}"),
    "not_created": "Игрок не создан.",
}

roles = {
    "set": string.Template("Статус ролей: Неофит: ${neofit}, Адепт: ${adept}, Мастер: ${master}"),
    "not_set": "Роли не установлены. Обратитесь к администратору для настройки бота.",
}

errors = {
    "unknown": "Произошла неизвестная ошибка.",
}
