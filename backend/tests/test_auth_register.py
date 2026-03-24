import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_register_user():
    email = f"testuser_{uuid.uuid4()}@example.com"
    with TestClient(app) as client:
        response = client.post(
            "/auth/register",
            json={"email": email, "password": "strongpassword123"},
        )
    assert response.status_code == 200
    assert response.json() == {"status": "user_created"}
