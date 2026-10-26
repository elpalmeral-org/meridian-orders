"""Salud, métricas, información y configuración."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect

from meridian_orders import main
from meridian_orders.config import normalize_database_url

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
