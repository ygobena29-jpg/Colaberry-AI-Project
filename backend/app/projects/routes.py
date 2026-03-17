from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.db import database
from app.auth.dependencies import get_current_user
from app.models.project import ProjectCreate, ProjectInDB

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

    result = await database["projects"].insert_one(doc)

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
