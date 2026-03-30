from typing import Any, Dict, List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

import app.db as db_module
from app.auth.dependencies import get_current_user
from app.models.project import ProjectInDB

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectInDB)
async def create_project(
    project: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    if db_module.database is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    if not project.get("name"):
        raise HTTPException(status_code=400, detail="Project name is required")

    user_id = current_user["sub"]

    project_doc = {
        "name": project.get("name"),
        "description": project.get("description"),
        "owner_id": user_id,
        "status": project.get("status", "active"),
        "members": [],
        "tags": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    result = await db_module.database["projects"].insert_one(project_doc)
    project_doc["_id"] = result.inserted_id

    return ProjectInDB(
        id=str(project_doc["_id"]),
        name=project_doc["name"],
        description=project_doc.get("description"),
        owner_id=project_doc["owner_id"],
        status=project_doc["status"],
        members=project_doc.get("members", []),
        tags=project_doc.get("tags", []),
        created_at=project_doc["created_at"],
        updated_at=project_doc["updated_at"],
    )


@router.get("/", response_model=List[ProjectInDB])
async def list_projects(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    if db_module.database is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    user_id = current_user["sub"]

    projects = []

    cursor = db_module.database["projects"].find({"owner_id": user_id})

    async for project in cursor:
        projects.append(
            ProjectInDB(
                id=str(project["_id"]),
                name=project["name"],
                description=project.get("description"),
                owner_id=project["owner_id"],
                status=project["status"],
                members=project.get("members", []),
                tags=project.get("tags", []),
                created_at=project["created_at"],
                updated_at=project["updated_at"],
            )
        )

    return projects
