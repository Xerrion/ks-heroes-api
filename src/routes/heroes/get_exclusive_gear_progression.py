"""Route for hero exclusive gear progression details."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from src.db.repositories.exclusive_gear import ExclusiveGearRepository
from src.db.repositories.hero import HeroRepository
from src.dependencies import get_supabase_client
from src.schemas.exclusive_gear import HeroExclusiveGearProgressionResponse
from supabase import Client

router = APIRouter()


@router.get(
    "/{hero_slug}/exclusive-gear/progression",
    response_model=HeroExclusiveGearProgressionResponse,
    summary="Get exclusive gear progression details",
)
async def get_hero_exclusive_gear_progression(
    hero_slug: str, supabase: Client = Depends(get_supabase_client)
):
    """
    Retrieve detailed progression information for a hero's exclusive gear (widget).

    Returns:
    - Current gear level and stats
    - Current skill tiers for both skills
    - Next upgrade information
    - Progression tracking

    **Widget/Gear Progression System:**
    - Level 0: Locked (needs materials to unlock level 1)
    - Level 1: Skill 1 Tier 1 unlocked + base stats
    - Level 2: Skill 2 Tier 1 unlocked + improved stats
    - Odd levels (3,5,7,9): Skill 1 upgrades tiers
    - Even levels (4,6,8,10): Skill 2 upgrades tiers
    """
    hero_repo = HeroRepository(supabase)
    hero = await run_in_threadpool(hero_repo.get_by_slug, hero_slug)

    if not hero:
        raise HTTPException(status_code=404, detail=f"Hero '{hero_slug}' not found")

    repository = ExclusiveGearRepository(supabase)

    try:
        data = await run_in_threadpool(repository.get_progression, hero["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not data:
        raise HTTPException(
            status_code=404, detail=f"No exclusive gear found for hero '{hero_slug}'"
        )

    return data
