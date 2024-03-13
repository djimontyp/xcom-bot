from pydantic import conint
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    # DB
    DB_URL: str = "postgresql+asyncpg://xcom:xcom@db:5432/xcom"
    POSTGRES_USER: str = "xcom"
    POSTGRES_PASSWORD: str = "xcom"
    POSTGRES_SERVER: str = "xcom"

    # Application
    REFRESH_TIME: int = 5  # seconds. время автообновления игроков в поиске.
    INVITE_TIMEOUT: int = 30  # seconds
    INVITE_COOLDOWN: int = 60  # seconds
    DELETE_AFTER: int = 30  # seconds. ephemeral messages. автоудаление сообщений от бота.

    # Discord
    DISCORD_BOT_TOKEN: str
    GUILD_ID: int

    # XCOM
    INITIAL_RATING: int = 1000
    RATING_DELTA: int = 2
    RATING_DEFAULT_MOVEMENT: int = 12

    ROLE_NEOFIT: int
    ROLE_ADEPT: int
    ROLE_MASTER: int
    ROLE_OFFICER: int
    ROLE_ARCHON: int
    ROLE_ETHEREAL: int

    SEARCH_MESSAGE__ETHEREAL: int
    SEARCH_MESSAGE__ARCHON: int
    SEARCH_MESSAGE__MASTER: int
    SEARCH_MESSAGE__OFFICER: int
    SEARCH_MESSAGE__ADEPT: int
    SEARCH_MESSAGE__NEOFIT: int

    LEADERBOARD_MESSAGE: int
    LEADERBOARD_COUNT: conint(ge=10, le=30) = 10
    LEADERBOARD_REFRESH_TIME: int = 3600

    SESSION_CHANNEL: int
    CATEGORY_FOR_VOICES_ID: int

    class Config:
        extra = "allow"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
