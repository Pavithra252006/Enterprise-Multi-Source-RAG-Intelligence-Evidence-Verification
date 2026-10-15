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
from typing import Any
from fastapi import Header, HTTPException, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, Chunk


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
        if normalized_allowed and user.role.lower().strip() not in normalized_allowed:
            return False

    return True


async def get_current_user(
    x_user_id: str | None = Header(None, alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency: resolves User from X-User-Id header.
    Accepts integer ID (e.g., '1', '4') or username ('intern', 'executive', etc.).
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required: Missing 'X-User-Id' header.",
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
