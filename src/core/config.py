from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    # Application
    DB_URL: str = "sqlite+aiosqlite:///database_xcom.sqlite3"
    REFRESH_TIME: int = 10  # seconds
    INVITE_TIMEOUT: int = 30  # seconds
    INVITE_COOLDOWN: int = 60  # seconds
    DELETE_AFTER: int = 30  # seconds. ephemeral messages

    # Discord
    DISCORD_BOT_TOKEN: str
    GUILD_ID: int

    # XCOM
    INITIAL_RATING: int
    RATING_DELTA: int = 5
    RATING_DEFAULT_MOVEMENT: int = 10

    ROLE_NEOFIT: int | None = 1195819868247830580
    ROLE_ADEPT: int | None = 1195819965304012833
    ROLE_MASTER: int | None = 1195820003514134579
    ROLE_OFFICER: int | None = None
    ROLE_ARCHON: int | None = None
    ROLE_ETHEREAL: int | None = None

    SESSION_CHANNEL: int | None = 1196106456974504096

    class Config:
        extra = "allow"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
