import os
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

import app.db as db_module
from app.models.user import UserCreate
from app.security.password import hash_password, verify_password
from app.security.jwt_tokens import issue_access_token
from app.auth.dependencies import get_current_user
from app.auth.rbac import require_roles

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register")
async def register(user: UserCreate):
    if db_module.database is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    existing = await db_module.database["users"].find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    doc = {
        "email": user.email,
        "hashed_password": hash_password(user.password),
        "roles": ["User"],
    }
    await db_module.database["users"].insert_one(doc)
    return {"status": "user_created"}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    if db_module.database is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    user_doc = await db_module.database["users"].find_one({"email": body.email})
    if not user_doc or not verify_password(body.password, user_doc["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    issuer = os.getenv("JWT_ISSUER", "local-nexus-auth")
    audience = os.getenv("JWT_AUDIENCE", "nexus-api")
    ttl = int(os.getenv("JWT_ACCESS_TTL_MINUTES", "15"))

    token = issue_access_token(
        user_id=str(user_doc["_id"]),
        org_id=str(user_doc.get("org_id", "")),
        roles=user_doc.get("roles", ["User"]),
        issuer=issuer,
        audience=audience,
        ttl_minutes=ttl,
        email=user_doc["email"],
    )

    return TokenResponse(access_token=token)


@router.get("/me")
def me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "user": {
            "email": current_user["email"],
            "roles": current_user.get("roles", []),
        }
    }


@router.get("/admin-test")
def admin_test(_: Dict[str, Any] = Depends(require_roles(["Admin"]))):
    return {"message": "admin access granted"}


@router.get("/test")
async def test_auth():
    return {"status": "auth working"}
