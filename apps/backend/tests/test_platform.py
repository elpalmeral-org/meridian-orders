"""Salud, métricas, información y configuración."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from meridian_orders import main, service
from meridian_orders.config import normalize_database_url
from meridian_orders.db import Base, get_engine

BACKEND = Path(__file__).resolve().parents[1]


def test_healthz(client: TestClient) -> None:
    assert client.get("/healthz").json() == {"status": "ok"}


def test_readyz_ok_with_database(client: TestClient) -> None:
    assert client.get("/readyz").status_code == 200


def test_readyz_unavailable_without_database(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    broken = create_engine("postgresql+psycopg://nadie:nada@127.0.0.1:1/ninguna")
    monkeypatch.setattr(main, "get_engine", lambda: broken)
    response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


def test_metrics_exposes_request_counter(client: TestClient) -> None:
    client.get("/api/orders")
    body = client.get("/metrics").text
    assert "meridian_http_requests_total" in body
    assert 'route="/api/orders"' in body


def test_info_reports_version(client: TestClient) -> None:
    body = client.get("/api/info").json()
    assert body["version"]
    assert body["environment"] == "local"


def test_get_engine_hides_parameters(client: TestClient) -> None:
    """El motor real de la app esconde los parámetros en los mensajes de error
    (corpus/03-data-classification.md §2). `client` ya disparó `get_engine()` una vez."""
    assert get_engine().hide_parameters is True


def test_hide_parameters_omits_values_from_db_errors() -> None:
    """Comprobación independiente del comportamiento de SQLAlchemy con hide_parameters=True:
    un fallo de BD no debe volcar customer_email en claro (corpus/03-data-classification.md §2).
    Motor propio, no el compartido por la app (que otros tests siguen usando)."""
    engine = create_engine("sqlite+pysqlite:///:memory:", hide_parameters=True)
    Base.metadata.create_all(engine)
    Base.metadata.drop_all(engine)  # fuerza "no such table: orders" al consultar
    session = sessionmaker(bind=engine)()
    try:
        with pytest.raises(OperationalError) as excinfo:
            service.list_orders(session, None, "compras@acme.example", 50, 0)
        assert "compras@acme.example" not in str(excinfo.value)
    finally:
        session.close()
        engine.dispose()


def test_dockerfile_disables_access_log() -> None:
    """--no-access-log: el log de acceso registraría customer_email en claro en la query string
    (corpus/03-data-classification.md §2)."""
    cmd_line = next(
        line for line in (BACKEND / "Dockerfile").read_text().splitlines() if line.startswith("CMD")
    )
    assert "--no-access-log" in cmd_line


def test_normalize_cnpg_url() -> None:
    assert (
        normalize_database_url("postgresql://app:x@orders-db-rw:5432/app")
        == "postgresql+psycopg://app:x@orders-db-rw:5432/app"
    )
    assert normalize_database_url("sqlite+pysqlite:///:memory:") == "sqlite+pysqlite:///:memory:"


def test_migrations_upgrade_and_downgrade(tmp_path: Path) -> None:
    url = f"sqlite+pysqlite:///{tmp_path / 'm.db'}"
    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", url)
    engine = create_engine(url)
    try:
        command.upgrade(cfg, "head")
        assert "orders" in inspect(engine).get_table_names()
        command.downgrade(cfg, "base")
        assert "orders" not in inspect(engine).get_table_names()
    finally:
        engine.dispose()
