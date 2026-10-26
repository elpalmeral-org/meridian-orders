"""Configuración por variables de entorno (prefijo MERIDIAN_)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MERIDIAN_")

    # En Kubernetes llega desde el Secret que genera CloudNativePG (clave "uri").
    # Por defecto, SQLite en memoria para desarrollo y tests.
    database_url: str = "sqlite+pysqlite:///:memory:"
    environment: str = "local"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def normalize_database_url(url: str) -> str:
    """CloudNativePG entrega `postgresql://…`; SQLAlchemy necesita el driver psycopg 3."""
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url
