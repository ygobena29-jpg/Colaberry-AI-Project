import os
from typing import Any, Dict

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.security.jwt_tokens import verify_access_token

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> Dict[str, Any]:
    if not credentials:
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token")

    issuer = os.getenv("JWT_ISSUER", "local-nexus-auth")
    audience = os.getenv("JWT_AUDIENCE", "nexus-api")

    try:
        payload = verify_access_token(credentials.credentials, issuer=issuer, audience=audience)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token")

    return payload
