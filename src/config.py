from pydantic import Extra
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./db.sqlite3"
    DISCORD_BOT_TOKEN: str
    GUILD_ID: int
    INITIAL_RATING: int

    class Config:
        extra = "allow"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
