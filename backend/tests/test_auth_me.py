import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_me_returns_current_user():
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "strongpassword123"

    with TestClient(app) as client:
        client.post("/auth/register", json={"email": email, "password": password})

        login_response = client.post("/auth/login", json={"email": email, "password": password})
        access_token = login_response.json()["access_token"]

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == email
    assert "roles" in data["user"]
