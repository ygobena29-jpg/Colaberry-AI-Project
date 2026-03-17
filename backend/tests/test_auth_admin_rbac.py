import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_normal_user_cannot_access_admin_endpoint():
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "strongpassword123"

    client.post("/auth/register", json={"email": email, "password": password})

    login_response = client.post("/auth/login", json={"email": email, "password": password})
    access_token = login_response.json()["access_token"]

    response = client.get(
        "/auth/admin-test",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}
