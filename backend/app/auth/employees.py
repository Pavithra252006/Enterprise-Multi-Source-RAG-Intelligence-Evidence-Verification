"""
auth/employees.py - Demo employee roster.

In a real deployment HR/IT would issue each employee a unique access code and
load them into the `employees` table. Each employee gets their OWN `users` row,
so query_logs.user_id identifies the individual (not just the role).
Only SHA-256 hashes of the codes are stored in the database.
"""
import hashlib

from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models import Employee, User

ROLE_CLEARANCE = {"Intern": 1, "Analyst": 2, "Manager": 3, "Executive": 4}

# (employee_id, full name, role, access code)
ROSTER = [
    ("EMP-1001", "Alex Chen", "Intern", "AC-7Q4M-2K9X"),
    ("EMP-1002", "Riya Sharma", "Intern", "RS-3F8P-6W1D"),
    ("EMP-2001", "Maya Patel", "Analyst", "MP-9T2L-5H7B"),
    ("EMP-2002", "Daniel Okoro", "Analyst", "DO-4N6V-8C3J"),
    ("EMP-3001", "David Kim", "Manager", "DK-1R5Y-7Z2G"),
    ("EMP-3002", "Priya Nair", "Manager", "PN-8B3S-4E6Q"),
    ("EMP-4001", "Elena Rostova", "Executive", "ER-6X1A-9M5T"),
]


def hash_code(code: str) -> str:
    return hashlib.sha256(code.strip().upper().encode()).hexdigest()


async def seed_employees() -> None:
    async with AsyncSessionLocal() as session:
        for emp_id, full_name, role, code in ROSTER:
            exists = await session.execute(select(Employee).where(Employee.employee_id == emp_id))
            if exists.scalar_one_or_none():
                continue
            username = emp_id.lower()
            res = await session.execute(select(User).where(User.name == username))
            user = res.scalar_one_or_none()
            if user is None:
                user = User(name=username, role=role, clearance_level=ROLE_CLEARANCE[role])
                session.add(user)
                await session.flush()
            session.add(
                Employee(
                    employee_id=emp_id,
                    full_name=full_name,
                    code_hash=hash_code(code),
                    user_id=user.id,
                )
            )
        await session.commit()
