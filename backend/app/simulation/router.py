"""
simulation/router.py – FastAPI router for What-If Policy Simulation endpoints.
"""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User
from app.simulation.engine import get_presets, simulate_policy_scenario
from app.simulation.schemas import PresetScenario, SimulationRequest, SimulationResult

log = logging.getLogger("simulation.router")

router = APIRouter()
api_router = APIRouter()


async def get_current_user(
    x_user_id: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve user from header or default to executive."""
    identifier = x_user_id or "executive"
    if identifier.isdigit():
        stmt = select(User).where(User.id == int(identifier))
    else:
        stmt = select(User).where(User.name == identifier.lower())
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        # Fallback to executive for simulation testing
        stmt = select(User).where(User.name == "executive")
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    if not user:
        user = User(id=4, name="executive", role="Executive", clearance_level=4)
    return user


@router.get("/presets", response_model=list[PresetScenario])
@api_router.get("/simulation/presets", response_model=list[PresetScenario])
async def list_presets() -> list[PresetScenario]:
    """Retrieve pre-configured enterprise policy scenarios for 1-click evaluation."""
    return get_presets()


@router.post("/simulate", response_model=SimulationResult)
@api_router.post("/simulation/simulate", response_model=SimulationResult)
async def run_simulation(
    request: SimulationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SimulationResult:
    """
    Simulates a counterfactual 'What-If' enterprise policy change,
    calculating downstream conflicts, affected documents, operational shifts,
    and recommended amendments across multi-source policies.
    """
    log.info("Running policy simulation for user '%s' (Clearance %d): %s", user.name, user.clearance_level, request.scenario[:60])
    return await simulate_policy_scenario(request.scenario, user=user, db=db)
