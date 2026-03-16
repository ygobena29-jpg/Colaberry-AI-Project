from __future__ import annotations

import os
import uuid

from fastapi import FastAPI

from app.db import connect_to_mongo, close_mongo_connection
import app.db as db_module
from app.security.jwt_tokens import issue_access_token, verify_access_token
from app.auth.routes import router as auth_router


app = FastAPI(title="Colaberry AI Project - Slice 1 (Auth + DB Foundation)")

app.include_router(auth_router)


@app.on_event("startup")
async def startup():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
async def health_db():
    if db_module.database is None:
        return {"status": "error", "db": "not connected"}

    await db_module.database.command("ping")
    return {"status": "ok", "db": "connected"}


@app.get("/health/crypto")
def health_crypto():
    issuer = os.getenv("JWT_ISSUER", "local-nexus-auth")
    audience = os.getenv("JWT_AUDIENCE", "nexus-api")
    ttl = int(os.getenv("JWT_ACCESS_TTL_MINUTES", "15"))

    user_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())

    token = issue_access_token(
        user_id=user_id,
        org_id=org_id,
        roles=["Admin"],
        issuer=issuer,
        audience=audience,
        ttl_minutes=ttl,
        email="test@example.com",
    )

    payload = verify_access_token(token, issuer=issuer, audience=audience)

    return {
        "status": "ok",
        "jwt_verified": True,
        "sub": payload.get("sub"),
        "org_id": payload.get("org_id"),
    }
