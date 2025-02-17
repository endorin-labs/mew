from functools import lru_cache
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()


class Settings:
    def __init__(self):
        self.db_user = os.getenv("DB_USER")
        self.db_host = os.getenv("DB_HOST")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_port = os.getenv("DB_PORT")
        self.db_name = os.getenv("DB_NAME")
        self.secret_key = os.getenv("SECRET_KEY")

        # validate required settings
        if not all(
            [
                self.db_user,
                self.db_host,
                self.db_password,
                self.db_port,
                self.db_name,
                self.secret_key,
            ]
        ):
            raise ValueError("Missing required environment variables")

    @property
    def supabase_postgres_url(self) -> str:
        escaped_password = quote_plus(self.db_password)
        return (
            f"postgresql+psycopg://{self.db_user}:{escaped_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def async_postgres_url(self) -> str:
        escaped_password = quote_plus(self.db_password)

        return (
            f"postgresql+asyncpg://{self.db_user}:{escaped_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
