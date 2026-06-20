from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, Request, status

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Use Bearer token authentication.",
        )
    role = settings.token_roles.get(token)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API token.",
        )
    return UserContext(role=role, token=token)


class InMemoryRateLimiter:
    def __init__(self, limit_per_minute: int) -> None:
        self.limit = limit_per_minute
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.time()
        window_start = now - 60
        bucket = self.requests[key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again shortly.",
            )
        bucket.append(now)


rate_limiter = InMemoryRateLimiter(settings.rate_limit_per_minute)


def enforce_rate_limit(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> UserContext:
    key = user.token if user.token != "anonymous" else request.client.host
    rate_limiter.check(key)
    return user
