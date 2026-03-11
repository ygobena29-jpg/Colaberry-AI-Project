from pydantic import BaseModel, EmailStr, Field
from typing import List


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserInDB(BaseModel):
    email: EmailStr
    hashed_password: str
    roles: List[str] = ["User"]
    