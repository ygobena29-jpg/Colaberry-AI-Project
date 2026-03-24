from datetime import datetime, timezone
from typing import Any, Dict, List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

import app.db as db_module
from app.auth.dependencies import get_current_user
from app.models.project import ProjectCreate, ProjectUpdate, ProjectInDB

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectInDB)
async def create_project(
    project: ProjectCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    owner_id = current_user["sub"]
    now = datetime.now(timezone.utc)

    doc = {
        "name": project.name,
        "description": project.description,
        "tags": project.tags,
        "owner_id": owner_id,
        "members": [owner_id],
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }

    result = await db_module.database["projects"].insert_one(doc)

    return ProjectInDB(
        id=str(result.inserted_id),
        name=doc["name"],
        description=doc["description"],
        owner_id=doc["owner_id"],
        status=doc["status"],
        members=doc["members"],
        tags=doc["tags"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.get("", response_model=List[ProjectInDB])
async def list_projects(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    user_id = current_user["sub"]

    cursor = db_module.database["projects"].find(
        {"$or": [{"owner_id": user_id}, {"members": user_id}]}
    )

    projects = []
    async for doc in cursor:
        projects.append(ProjectInDB(
            id=str(doc["_id"]),
            name=doc["name"],
            description=doc["description"],
            owner_id=doc["owner_id"],
            status=doc["status"],
            members=doc["members"],
            tags=doc["tags"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        ))

    return projects


@router.patch("/{project_id}", response_model=ProjectInDB)
async def update_project(
    project_id: str,
    update: ProjectUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    user_id = current_user["sub"]

    try:
        oid = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project ID")

    doc = await db_module.database["projects"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    if doc["owner_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not project owner")

    changes = {k: v for k, v in update.model_dump().items() if v is not None}
    changes["updated_at"] = datetime.now(timezone.utc)

    await db_module.database["projects"].update_one({"_id": oid}, {"$set": changes})
    doc.update(changes)

    return ProjectInDB(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc["description"],
        owner_id=doc["owner_id"],
        status=doc["status"],
        members=doc["members"],
        tags=doc["tags"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    user_id = current_user["sub"]

    try:
        oid = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project ID")

    doc = await db_module.database["projects"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    if doc["owner_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not project owner")

    await db_module.database["projects"].delete_one({"_id": oid})
