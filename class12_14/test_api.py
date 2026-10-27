import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_requests_have_different_ids(client):
    first = client.get("/health")
    second = client.get("/health")

    assert first.headers["X-Request-ID"] != second.headers["X-Request-ID"]
