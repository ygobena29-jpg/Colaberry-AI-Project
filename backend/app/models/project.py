from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    active = "active"
    archived = "archived"
    completed = "completed"
    deleted = "deleted"


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3)
    description: str
    tags: List[str] = []


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3)
    description: str | None = None
    tags: List[str] | None = None
    status: ProjectStatus | None = Field(
        default=None,
        description="Cannot be set to 'deleted' via PATCH — use DELETE instead.",
    )


class ProjectInDB(BaseModel):
    id: str
    name: str
    description: str | None = None
    owner_id: str
    status: str = "active"
    members: List[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
