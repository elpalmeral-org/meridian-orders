"""Entorno de Alembic: usa la misma configuración que la aplicación."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from meridian_orders import models  # noqa: F401  (registra las tablas en Base.metadata)
from meridian_orders.config import get_settings, normalize_database_url
from meridian_orders.db import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
url = config.get_main_option("sqlalchemy.url") or normalize_database_url(
    get_settings().database_url
)


def run_migrations_offline() -> None:
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
