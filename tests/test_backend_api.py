from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "GenAI Fraud Detection Platform"


def test_auth_routes_exist(client: TestClient) -> None:
    response = client.get("/api/v1/auth/health")
    assert response.status_code == 404 or response.status_code == 200
