"""
auth/router.py - User lookup and clearance-level endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.access import create_token, get_current_user
from app.auth.employees import hash_code
from app.db import get_db
from app.models import Employee, LoginEvent, User
from app.schemas import UserRead

router = APIRouter()


class LoginRequest(BaseModel):
    access_code: str


def _profile(user: User, emp: Employee | None) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "role": user.role,
        "clearance_level": user.clearance_level,
        "employee_id": emp.employee_id if emp else None,
        "full_name": emp.full_name if emp else user.name,
    }


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Exchange an individual, company-issued access code for a session token."""
    res = await db.execute(
        select(Employee).where(Employee.code_hash == hash_code(body.access_code))
    )
    emp = res.scalar_one_or_none()
    if emp is None or not emp.active:
        db.add(LoginEvent(employee_id=emp.employee_id if emp else None, success=False))
        await db.commit()
        raise HTTPException(status_code=401, detail="Invalid access code.")
    user = (await db.execute(select(User).where(User.id == emp.user_id))).scalar_one()
    db.add(LoginEvent(employee_id=emp.employee_id, success=True))
    await db.commit()
    return {"token": create_token(user.id), "user": _profile(user, emp)}


@router.get("/me")
async def me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    emp = (await db.execute(select(Employee).where(Employee.user_id == user.id))).scalar_one_or_none()
    return _profile(user, emp)


@router.get("/audit/logins")
async def login_audit(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Who logged in and when (Executive only)."""
    if user.clearance_level < 4:
        raise HTTPException(status_code=403, detail="Executive access required.")
    rows = (await db.execute(select(LoginEvent).order_by(LoginEvent.id.desc()).limit(100))).scalars().all()
    return [
        {"employee_id": r.employee_id, "success": r.success, "at": r.created_at.isoformat()}
        for r in rows
    ]



@router.get("/ping")
async def ping():
    return {"module": "auth", "status": "stub - not yet implemented"}


@router.get("/users", response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_db)):
    """Return all demo users (no real auth - demo only)."""
    result = await db.execute(select(User))
    return result.scalars().all()


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Return a single user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user