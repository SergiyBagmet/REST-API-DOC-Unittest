import pathlib
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PG_DB: str = "name_database"
    PG_USER: str = "user_database"
    PG_PASSWORD: int = 123456
    PG_DOMAIN: str = "localhost"
    PG_PORT: int = 5432

    DB_URL: str = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_DOMAIN}:{PG_PORT}/{PG_DB}"

    PG_TEST_DB: str = "name_test_database"
    PG_TEST_USER: str = "user_test_database"
    PG_TEST_PASSWORD: int = 123456
    PG_TEST_DOMAIN: str = "localhost"
    PG_TEST_PORT: int = 5432

    DB_TEST_URL: str = f"postgresql+asyncpg://{PG_TEST_USER}:{PG_TEST_PASSWORD}@{PG_TEST_DOMAIN}:{PG_TEST_PORT}/{PG_TEST_DB}"

    SECRET_KEY_JWT: str = "secret_key_jwt"
    ALGORITHM_JWT: str = "HS256"

    MAIL_USERNAME: str = "example@meta.ua"
    MAIL_PASSWORD: str = "secretPassword"
    MAIL_FROM: str = "example@meta.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"

    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: int = 123456

    CLOUDINARY_NAME: str = "cloud_name"
    CLOUDINARY_API_KEY: int = 123456
    CLOUDINARY_API_SECRET: str = "api_secret"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_prefix="",
        env_file_encoding="utf-8",
        env_file=pathlib.Path(__file__).parent.parent.parent / ".env",
        extra='ignore',
    )


config = Settings()
