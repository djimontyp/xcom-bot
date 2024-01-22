from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./db.sqlite3"
    DISCORD_BOT_TOKEN: str
    GUILD_ID: int
    INITIAL_RATING: int
    REFRESH_SESSION_MESSAGES_INTERVAL: int = 10  # seconds
    INVITE_TIMEOUT: int = 30  # seconds,
    COOLDOWN_INVITE: int = 60  # seconds
    DELETE_AFTER: int = 30  # seconds for ephemeral messages
    RATING_DELTA: int = 5
    RATING_DEFAULT_MOVEMENT: int = 10

    class Config:
        extra = "allow"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
