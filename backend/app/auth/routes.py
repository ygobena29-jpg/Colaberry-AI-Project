import os

from typing import Any, Dict

from pymongo.errors import DuplicateKeyError

from fastapi import APIRouter, Depends, HTTPException
from app.models.user import UserCreate
from app.db import database
from app.security.password import hash_password, verify_password
from app.security.jwt_tokens import issue_access_token
from app.auth.dependencies import get_current_user
from app.auth.rbac import require_roles

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

    try:
        await database.users.insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")

    return {"status": "user_created"}


@router.post("/login")
async def login(user: UserCreate):
    record = await database.users.find_one({"email": user.email})

    if not record:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, record["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    issuer = os.getenv("JWT_ISSUER", "local-nexus-auth")
    audience = os.getenv("JWT_AUDIENCE", "nexus-api")
    ttl = int(os.getenv("JWT_ACCESS_TTL_MINUTES", "15"))

    token = issue_access_token(
        user_id=str(record["_id"]),
        org_id=str(record.get("org_id", "")),
        roles=record.get("roles", ["User"]),
        issuer=issuer,
        audience=audience,
        ttl_minutes=ttl,
        email=record["email"],
    )

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {"user": current_user}


@router.get("/admin-test")
def admin_test(current_user: Dict[str, Any] = Depends(require_roles(["Admin"]))):
    return {"message": "admin access granted"}
