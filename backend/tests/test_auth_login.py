import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_user():
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "strongpassword123"

    client.post("/auth/register", json={"email": email, "password": password})

    response = client.post("/auth/login", json={"email": email, "password": password})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
