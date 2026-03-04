import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client: AsyncIOMotorClient | None = None
database = None


async def connect_to_mongo():
    global client, database
    client = AsyncIOMotorClient(MONGO_URL)
    database = client["architectos"]
    print("✅ Connected to MongoDB")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("❌ MongoDB connection closed")
        from fastapi import FastAPI
from app.db import connect_to_mongo, close_mongo_connection, database

app = FastAPI()


@app.on_event("startup")
async def startup():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/db")
async def health_db():
    if database is None:
        return {"status": "error", "db": "not connected"}

    await database.command("ping")
    return {"status": "ok", "db": "connected"}
from __future__ import annotations

import os
import uuid

from fastapi import FastAPI

from app.db import connect_to_mongo, close_mongo_connection, database
from app.security.jwt_tokens import issue_access_token, verify_access_token

app = FastAPI(title="Colaberry AI Project - Slice 1 (Auth + DB Foundation)")


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
    if database is None:
        return {"status": "error", "db": "not connected"}

    await database.command("ping")
    return {"status": "ok", "db": "connected"}


@app.get("/health/crypto")
def health_crypto():
    """
    Proves RS256 wiring works INSIDE the container by:
    - loading RSA keys from /run/secrets/...
    - issuing a JWT
    - verifying the JWT
    """
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
