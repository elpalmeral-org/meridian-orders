"""Escenarios de openspec/specs/orders/spec.md."""

import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient

NEW_ORDER: dict[str, Any] = {
    "customer_name": "Acme Logística",
    "customer_email": "compras@acme.example",
    "total_amount": "149.90",
}


def create(client: TestClient, **overrides: Any) -> dict[str, Any]:
    response = client.post("/api/orders", json={**NEW_ORDER, **overrides})
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


# Requisito: crear pedidos
def test_create_order_starts_pending_in_eur(client: TestClient) -> None:
    order = create(client)
    assert order["status"] == "pending"
    assert order["currency"] == "EUR"
    assert order["total_amount"] == "149.90"


@pytest.mark.parametrize(
    "overrides",
    [
        {"total_amount": "0"},
        {"total_amount": "-5"},
        {"customer_email": "no-es-un-email"},
        {"customer_name": "   "},
        {"currency": "euro"},
    ],
)
def test_create_order_rejects_invalid_data(client: TestClient, overrides: dict[str, Any]) -> None:
    response = client.post("/api/orders", json={**NEW_ORDER, **overrides})
    assert response.status_code == 422


# Requisito: consultar pedidos
def test_get_order_by_id(client: TestClient) -> None:
    order = create(client)
    response = client.get(f"/api/orders/{order['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == order["id"]


def test_get_unknown_order_returns_404(client: TestClient) -> None:
    assert client.get(f"/api/orders/{uuid.uuid4()}").status_code == 404


def test_list_orders_filters_by_status_and_paginates(client: TestClient) -> None:
    first = create(client)
    create(client, customer_name="Beta SL")
    client.patch(f"/api/orders/{first['id']}/status", json={"status": "confirmed"})

    everything = client.get("/api/orders").json()
    assert everything["total"] == 2

    confirmed = client.get("/api/orders", params={"status": "confirmed"}).json()
    assert confirmed["total"] == 1
    assert confirmed["items"][0]["id"] == first["id"]

    page = client.get("/api/orders", params={"limit": 1}).json()
    assert len(page["items"]) == 1
    assert page["total"] == 2


# Requisito: ciclo de vida del pedido
@pytest.mark.parametrize(
    "path",
    [
        ["confirmed", "shipped"],
        ["cancelled"],
        ["confirmed", "cancelled"],
    ],
)
def test_allowed_transitions(client: TestClient, path: list[str]) -> None:
    order = create(client)
    for target in path:
        response = client.patch(f"/api/orders/{order['id']}/status", json={"status": target})
        assert response.status_code == 200, response.text
        assert response.json()["status"] == target


@pytest.mark.parametrize(
    ("path", "forbidden"),
    [
        ([], "shipped"),  # no se envía sin confirmar
        (["confirmed", "shipped"], "cancelled"),  # enviado es final
        (["cancelled"], "confirmed"),  # cancelado es final
        ([], "pending"),  # no hay vuelta atrás a pending
    ],
)
def test_forbidden_transitions_return_409(
    client: TestClient, path: list[str], forbidden: str
) -> None:
    order = create(client)
    for target in path:
        client.patch(f"/api/orders/{order['id']}/status", json={"status": target})
    response = client.patch(f"/api/orders/{order['id']}/status", json={"status": forbidden})
    assert response.status_code == 409


def test_change_status_of_unknown_order_returns_404(client: TestClient) -> None:
    response = client.patch(f"/api/orders/{uuid.uuid4()}/status", json={"status": "confirmed"})
    assert response.status_code == 404
