import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_create_project_returns_expected_fields():
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "strongpassword123"

    with TestClient(app) as client:
        client.post("/auth/register", json={"email": email, "password": password})

        login_response = client.post("/auth/login", json={"email": email, "password": password})
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = client.post(
            "/projects",
            json={"name": "My First Project", "description": "A test project", "tags": ["ai", "test"]},
            headers=headers,
        )
        assert create_response.status_code == 200

        project = create_response.json()
        assert "id" in project
        assert project["name"] == "My First Project"
        assert project["description"] == "A test project"
        assert "owner_id" in project
        assert project["status"] == "active"
        assert "created_at" in project
        assert "updated_at" in project


def test_list_projects_includes_created_project():
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "strongpassword123"

    with TestClient(app) as client:
        client.post("/auth/register", json={"email": email, "password": password})

        login_response = client.post("/auth/login", json={"email": email, "password": password})
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = client.post(
            "/projects",
            json={"name": "Listable Project", "description": "Should appear in list", "tags": []},
            headers=headers,
        )
        assert create_response.status_code == 200
        project_id = create_response.json()["id"]

        list_response = client.get("/projects", headers=headers)
        assert list_response.status_code == 200

        project_ids = [p["id"] for p in list_response.json()]
        assert project_id in project_ids
