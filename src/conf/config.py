import pathlib

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PG_DB: str = "name_database"
    PG_USER: str = "user_database"
    PG_PASSWORD: int = 123456
    PG_DOMAIN: str = "localhost"
    PG_PORT: int = 5432

    DB_URL: PostgresDsn = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_DOMAIN}:{PG_PORT}/{PG_DB}"

    SECRET_KEY_JWT: str = "secret_key_jwt"
    ALGORITHM_JWT: str = "HS256"

    model_config = SettingsConfigDict(env_file='.env', extra='ignore', env_file_encoding='utf-8')


dot_env_file = pathlib.Path(__file__).parent.parent.parent / '.env'
config = Settings(_env_file=dot_env_file)
