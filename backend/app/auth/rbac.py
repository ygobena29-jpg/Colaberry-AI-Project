from typing import Any, Callable, Dict, List

from fastapi import Depends, HTTPException

from app.auth.dependencies import get_current_user


def require_roles(allowed_roles: List[str]) -> Callable:
    def dependency(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_roles: List[str] = current_user.get("roles", [])
        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return dependency
