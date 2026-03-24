import os
import uuid

from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.main import app
from app.security.password import hash_password


def test_admin_user_can_access_admin_endpoint():
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "strongpassword123"

    # Insert admin user via sync PyMongo — avoids async event loop conflict
    # with the app's Motor client. PyMongo is already installed as a Motor dependency.
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    sync_client = MongoClient(mongo_url)
    sync_client["architectos"]["users"].insert_one({
        "email": email,
        "hashed_password": hash_password(password),
        "roles": ["Admin"],
    })
    sync_client.close()

    with TestClient(app) as client:
        login_response = client.post("/auth/login", json={"email": email, "password": password})
        access_token = login_response.json()["access_token"]

        response = client.get(
            "/auth/admin-test",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 200
    assert response.json() == {"message": "admin access granted"}
