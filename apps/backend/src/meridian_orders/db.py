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
    url = normalize_database_url(get_settings().database_url)
    if url.startswith("sqlite") and ":memory:" in url:
        # Una única conexión compartida: la base en memoria sobrevive entre peticiones.
        return create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    return create_engine(url, pool_pre_ping=True)


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_session() -> Iterator[Session]:
    with get_sessionmaker()() as session:
        yield session
