from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3)
    description: str
    tags: List[str] = []


class ProjectInDB(BaseModel):
    id: str
    name: str
    description: str
    owner_id: str
    status: str = "active"
    members: List[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
