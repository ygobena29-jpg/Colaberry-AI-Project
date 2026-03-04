from __future__ import annotations

import os
import uuid

from fastapi import FastAPI

from app.security.jwt_tokens import issue_access_token, verify_access_token

app = FastAPI(title="Colaberry AI Project - Slice 1 (Auth Foundation)")


@app.get("/health")
def health():
    return {"status": "ok"}


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
