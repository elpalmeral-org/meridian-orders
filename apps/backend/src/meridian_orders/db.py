"""Motor y sesiones de SQLAlchemy."""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from meridian_orders.config import get_settings, normalize_database_url


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine() -> Engine:
    # hide_parameters: si una consulta falla, SQLAlchemy no mete los valores de los parámetros
    # (p. ej. customer_email, dato C3) en el mensaje de la excepción (clasificación de datos §2).
    url = normalize_database_url(get_settings().database_url)
    if url.startswith("sqlite") and ":memory:" in url:
        # Una única conexión compartida: la base en memoria sobrevive entre peticiones.
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            hide_parameters=True,
        )
    return create_engine(url, pool_pre_ping=True, hide_parameters=True)


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_session() -> Iterator[Session]:
    with get_sessionmaker()() as session:
        yield session
