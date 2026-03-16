import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_user():
    email = f"testuser_{uuid.uuid4()}@example.com"
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "strongpassword123"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "user_created"}
