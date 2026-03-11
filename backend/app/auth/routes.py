from fastapi import APIRouter, HTTPException
from app.models.user import UserCreate
from app.db import database
from app.security.password import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(user: UserCreate):
    existing = await database.users.find_one({"email": user.email})

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)

    user_doc = {
        "email": user.email,
        "hashed_password": hashed,
        "roles": ["User"]
    }

    await database.users.insert_one(user_doc)

    return {"status": "user_created"}
