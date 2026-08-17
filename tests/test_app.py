from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "version" in body
    assert "hostname" in body
    assert body["message"] == "ReleaseForge Demo Application"


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_payment_success_when_not_simulating_failure():
    response = client.get("/payment")
    assert response.status_code == 200
    assert response.json()["status"] == "success"