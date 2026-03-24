import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_patch_project_updates_name_and_description():
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "strongpassword123"

    with TestClient(app) as client:
        client.post("/auth/register", json={"email": email, "password": password})

        login_response = client.post("/auth/login", json={"email": email, "password": password})
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = client.post(
            "/projects",
            json={"name": "Original Name", "description": "Original description", "tags": []},
            headers=headers,
        )
        assert create_response.status_code == 200
        created = create_response.json()
        project_id = created["id"]
        owner_id = created["owner_id"]

        patch_response = client.patch(
            f"/projects/{project_id}",
            json={"name": "Updated Name", "description": "Updated description"},
            headers=headers,
        )
        assert patch_response.status_code == 200
        updated = patch_response.json()

        assert updated["id"] == project_id
        assert updated["owner_id"] == owner_id
        assert updated["name"] == "Updated Name"
        assert updated["description"] == "Updated description"
