from typing import Any, Dict, List
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Response

import app.db as db_module
from app.auth.dependencies import get_current_user
from app.models.project import ProjectCreate, ProjectInDB, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectInDB)
async def create_project(
    project: ProjectCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    if db_module.database is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    user_id = current_user["sub"]

    now = datetime.now(timezone.utc)
    project_doc = {
        "name": project.name,
        "description": project.description,
        "owner_id": user_id,
        "status": "active",
        "members": [],
        "tags": project.tags,
        "created_at": now,
        "updated_at": now,
    }

    result = await db_module.database["projects"].insert_one(project_doc)
    project_doc["_id"] = result.inserted_id

    return ProjectInDB(
        id=str(project_doc["_id"]),
        name=project_doc["name"],
        description=project_doc["description"],
        owner_id=project_doc["owner_id"],
        status=project_doc["status"],
        members=project_doc["members"],
        tags=project_doc["tags"],
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

    cursor = db_module.database["projects"].find(
        {"owner_id": user_id, "status": {"$ne": "deleted"}}
    )

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


@router.patch("/{project_id}", response_model=ProjectInDB)
async def update_project(
    project_id: str,
    updates: ProjectUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    if db_module.database is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    try:
        oid = ObjectId(project_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid project ID")

    user_id = current_user["sub"]

    existing = await db_module.database["projects"].find_one(
        {"_id": oid, "owner_id": user_id}
    )
    if existing is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if existing.get("status") == "deleted":
        raise HTTPException(status_code=409, detail="Cannot update a deleted project")

    patch = {k: v for k, v in updates.model_dump().items() if v is not None}

    if patch.get("status") == "deleted":
        raise HTTPException(
            status_code=400, detail="Use DELETE to remove a project"
        )
    if not patch:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    patch["updated_at"] = datetime.now(timezone.utc)

    await db_module.database["projects"].update_one({"_id": oid}, {"$set": patch})

    updated = await db_module.database["projects"].find_one({"_id": oid})

    return ProjectInDB(
        id=str(updated["_id"]),
        name=updated["name"],
        description=updated.get("description"),
        owner_id=updated["owner_id"],
        status=updated["status"],
        members=updated.get("members", []),
        tags=updated.get("tags", []),
        created_at=updated["created_at"],
        updated_at=updated["updated_at"],
    )


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    if db_module.database is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    try:
        oid = ObjectId(project_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid project ID")

    user_id = current_user["sub"]

    existing = await db_module.database["projects"].find_one(
        {"_id": oid, "owner_id": user_id}
    )
    if existing is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if existing.get("status") == "deleted":
        raise HTTPException(status_code=409, detail="Project is already deleted")

    now = datetime.now(timezone.utc)
    await db_module.database["projects"].update_one(
        {"_id": oid},
        {"$set": {"status": "deleted", "deleted_at": now, "updated_at": now}},
    )

    return Response(status_code=204)
