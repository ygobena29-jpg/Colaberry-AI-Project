import asyncio
import uuid

from fastapi.testclient import TestClient

import app.db as db_module
from app.main import app
from app.security.password import hash_password

client = TestClient(app)


def test_admin_user_can_access_admin_endpoint():
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "strongpassword123"

    async def insert_admin():
        await db_module.database["users"].insert_one({
            "email": email,
            "hashed_password": hash_password(password),
            "roles": ["Admin"],
        })

    # Trigger app startup so db_module.database is initialised
    client.get("/health")
    asyncio.run(insert_admin())

    login_response = client.post("/auth/login", json={"email": email, "password": password})
    access_token = login_response.json()["access_token"]

    response = client.get(
        "/auth/admin-test",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "admin access granted"}
