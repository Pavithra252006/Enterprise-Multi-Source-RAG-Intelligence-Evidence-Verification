#!/usr/bin/env python3
"""
seed.py – Standalone script to verify DB connectivity and seed the 4 demo users.
Run AFTER PostgreSQL is up:  python backend/seed.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select, text
from app.db import AsyncSessionLocal, init_db
from app.models import User

DEMO_USERS = [
    {"name": "intern", "role": "Intern", "clearance_level": 1},
    {"name": "analyst", "role": "Analyst", "clearance_level": 2},
    {"name": "manager", "role": "Manager", "clearance_level": 3},
    {"name": "executive", "role": "Executive", "clearance_level": 4},
]


async def main():
    print("Initialising database tables...")
    await init_db()
    print("Tables created (or already exist).")

    async with AsyncSessionLocal() as session:
        # Verify connectivity
        await session.execute(text("SELECT 1"))
        print("Database connection: OK")

        # Seed users
        for data in DEMO_USERS:
            result = await session.execute(select(User).where(User.name == data["name"]))
            if result.scalar_one_or_none() is None:
                session.add(User(**data))
                print(f"  Inserted user: {data['name']} (clearance={data['clearance_level']})")
            else:
                print(f"  User already exists: {data['name']}")
        await session.commit()

        # Verify
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"\nUsers in DB ({len(users)} total):")
        for u in users:
            print(f"  id={u.id}  name={u.name}  role={u.role}  clearance={u.clearance_level}")

    print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(main())
