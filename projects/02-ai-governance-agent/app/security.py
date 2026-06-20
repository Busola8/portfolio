from __future__ import annotations

from dataclasses import dataclass

from fastapi import Header, HTTPException, status

from .settings import settings


@dataclass(frozen=True)
class UserContext:
    role: str
    token: str


def get_current_user(authorization: str | None = Header(default=None)) -> UserContext:
    if not authorization:
        return UserContext(role="demo", token="anonymous")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Use Bearer auth.")
    role = settings.token_roles.get(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token.")
    return UserContext(role=role, token=token)
