import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_delete_project_removes_it_from_list():
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "strongpassword123"

    with TestClient(app) as client:
        client.post("/auth/register", json={"email": email, "password": password})

        login_response = client.post("/auth/login", json={"email": email, "password": password})
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = client.post(
            "/projects",
            json={"name": "Delete Me", "description": "Temporary project", "tags": ["test"]},
            headers=headers,
        )
        assert create_response.status_code == 200
        project_id = create_response.json()["id"]

        delete_response = client.delete(f"/projects/{project_id}", headers=headers)
        assert delete_response.status_code == 204

        list_response = client.get("/projects", headers=headers)
        assert list_response.status_code == 200
        project_ids = [p["id"] for p in list_response.json()]
        assert project_id not in project_ids
