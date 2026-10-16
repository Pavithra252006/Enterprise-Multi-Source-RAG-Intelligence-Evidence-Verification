"""
auth/access.py – Access control, clearance level enforcement, and user resolution.

Access rules:
1 = public       (intern)
2 = internal     (analyst)
3 = confidential (manager)
4 = restricted   (executive)

can_access rule:
clearance_level >= chunk.access_level AND (allowed_roles is empty/None OR user.role in allowed_roles)
"""
import base64
import hashlib
import hmac
import os
import time
from typing import Any
from fastapi import Header, HTTPException, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, Chunk

_SECRET = os.getenv("AUTH_SECRET", "dev-only-change-me").encode()
TOKEN_TTL = 8 * 3600


def create_token(user_id: int) -> str:
    payload = f"{user_id}:{int(time.time()) + TOKEN_TTL}"
    sig = hmac.new(_SECRET, payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}:{sig}".encode()).decode()


def verify_token(token: str) -> int | None:
    try:
        uid, exp, sig = base64.urlsafe_b64decode(token.encode()).decode().split(":")
        expected = hmac.new(_SECRET, f"{uid}:{exp}".encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(sig, expected) and int(exp) > time.time():
            return int(uid)
    except Exception:  # noqa: BLE001
        pass
    return None


def can_access(user: User, chunk: Chunk | dict[str, Any]) -> bool:
    """
    Returns True if the user has sufficient clearance and matching role permissions.
    Restricted chunks must NEVER be returned if this returns False.
    """
    if isinstance(chunk, dict):
        access_level = chunk.get("access_level", 1)
        allowed_roles = chunk.get("allowed_roles")
    else:
        access_level = getattr(chunk, "access_level", 1)
        allowed_roles = getattr(chunk, "allowed_roles", None)

    # 1. Clearance check
    if user.clearance_level < access_level:
        return False

    # 2. Role check (if allowed_roles is specified)
    if allowed_roles:
        normalized_allowed = [r.lower().strip() for r in allowed_roles if r]
        user_role = (user.role or user.name or "").lower().strip()
        if normalized_allowed and user_role not in normalized_allowed:
            return False

    return True


async def get_current_user(
    x_user_id: str | None = Header(None, alias="X-User-Id"),
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency: resolves User from 'Authorization: Bearer <token>' (login),
    falling back to X-User-Id (integer ID or username) for scripts.
    """
    if authorization and authorization.lower().startswith("bearer "):
        uid = verify_token(authorization[7:].strip())
        if uid is None:
            raise HTTPException(status_code=401, detail="Invalid or expired session.")
        result = await db.execute(select(User).where(User.id == uid))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=401, detail="User no longer exists.")
        return user

    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required: please log in.",
        )

    user: User | None = None

    # Check if x_user_id is numeric ID
    if x_user_id.isdigit():
        uid = int(x_user_id)
        result = await db.execute(select(User).where(User.id == uid))
        user = result.scalar_one_or_none()
    else:
        # Check by username case-insensitively
        result = await db.execute(
            select(User).where(func.lower(User.name) == x_user_id.lower().strip())
        )
        user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"User with identifier '{x_user_id}' not found.",
        )

    return user
