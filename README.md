# Как запустить проект

### Собрать образ из Dockerfile

```bash
docker build -t 'xcom:latest' .
```

### Запустить контейнер

На Windows:

```bash
docker run -v ${PWD}/src:/xcom/src -v ${PWD}/.env:/xcom/.env -v ${PWD}/requirements.txt:/xcom/requirements.txt xcom:latest
```

На Mac / Linux:

```bash
docker run -v "$(pwd)"/src:/xcom/src -v "$(pwd)"/.env:/xcom/.env -v "$(pwd)"/requirements.txt:/xcom/requirements.txt xcom:latest
```

---

# Описание

Бот в Discord для учета рейтинга игроков и создания игровых сессий на основе рейтинга игроков.

# Функционал:

| Feature                        |   Group   |        Command        |                          Options                          |   Permission    | Описание                                                                                  | 
|:-------------------------------|:---------:|:---------------------:|:---------------------------------------------------------:|:---------------:|-------------------------------------------------------------------------------------------|
| Добавить игрока                | `/player` |        `start`        |                             -                             |    `Player`     | Добавляет игрока<br/>Добавляет роль **"Неофит"**<br/>Если игрок уже в базе - не добавляет |
| Начать поиск сессии            | `/player` |         `go`          |                             -                             |    `Player`     | Начинает поиск сессии                                                                     |
| Установить роли в бота         | `/admin`  |      `set_roles`      | [neofit](#Options), [adept](#Options), [master](#Options) | `Administrator` | Бот запоминает роли которые нужно будет назначать игрокам.                                |
| Посмотреть роли                | `/admin`  |        `roles`        |                                                           | `Administrator` | Посмотреть роли которые нужно будет назначать игрокам.                                    |
| Установить канал поиска сессии | `/admin`  | `set_session_channel` |                    [channel](#Options)                    | `Administrator` | Бот запоминает канал в котором будет происходить поиск сессии.                            |
| Посмотреть канал поиска сессии | `/admin`  |   `session_channel`   |                                                           | `Administrator` | Посмотреть канал в котором будет происходить поиск сессии.                                |
| Сообщение для поиска сессии    | `/admin`  |   `session_message`   |                     [rank](#Options)                      | `Administrator` | Вызвать сообщение для поиска сессии с авто обновлением для ранга.                         |

---

### Options:

- `neofit`[Role] - _Роль для новых игроков 0-199 рейтинга._
- `adept`[Role] - _Роль для игроков 200-499 рейтинга._
- `master`[Role] - _Роль для игроков 500-999 рейтинга._
- `channel`[TextChannel] - _Канал в котором будет происходить поиск сессии._
- `rank`[Rank] - _Ранг игрока._
