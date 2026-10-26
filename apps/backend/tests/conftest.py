from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from meridian_orders.db import Base, get_engine
from meridian_orders.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = get_engine()  # SQLite en memoria por defecto (MERIDIAN_DATABASE_URL sin definir)
    Base.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(engine)
