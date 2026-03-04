from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

import jwt  # PyJWT

from app.security.jwt_keys import load_rsa_keys


def issue_access_token(
    *,
    user_id: str,
    org_id: str,
    roles: List[str],
    issuer: str,
    audience: str,
    ttl_minutes: int = 15,
    email: Optional[str] = None,
) -> str:
    private_key, _ = load_rsa_keys()

    now = int(time.time())
    payload: Dict[str, Any] = {
        "iss": issuer,
        "aud": audience,
        "sub": user_id,
        "org_id": org_id,
        "roles": roles,
        "iat": now,
        "exp": now + (ttl_minutes * 60),
        "jti": str(uuid.uuid4()),
    }
    if email:
        payload["email"] = email

    return jwt.encode(payload, private_key, algorithm="RS256")


def verify_access_token(
    token: str,
    *,
    issuer: str,
    audience: str,
) -> Dict[str, Any]:
    _, public_key = load_rsa_keys()
    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        issuer=issuer,
        audience=audience,
    )
