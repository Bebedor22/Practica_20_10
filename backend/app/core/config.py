from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://roadmap:roadmap@localhost:5432/roadmap_cursos"
    )
    test_database_url: str = (
        "postgresql+psycopg://roadmap:roadmap@localhost:5432/roadmap_cursos_test"
    )
    jwt_secret: str = "dev-secret-change-me-please-32-bytes-minimum"
    jwt_expires_minutes: int = 1440
    seed_data: bool = True

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
