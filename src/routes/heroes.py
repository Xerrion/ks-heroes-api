"""Heroes endpoints optimized for the public data API.

Provides hero collection and per-hero nested resources (skills, stats, talents,
exclusive gear) so clients such as the simulator, wiki tools, or dashboards can
fetch everything from a single namespace.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.concurrency import run_in_threadpool

from src.db.repositories.exclusive_gear import ExclusiveGearRepository
from src.db.repositories.hero import HeroRepository
from src.db.repositories.skills import SkillsRepository
from src.db.repositories.stats import (
    HeroConquestStatsRepository,
    HeroExpeditionStatsRepository,
)
from src.db.repositories.talent import TalentRepository
from src.dependencies import (
    get_conquest_stats_repository,
    get_exclusive_gear_repository,
    get_expedition_stats_repository,
    get_hero_repository,
    get_skills_repository,
    get_talent_repository,
)
from src.schemas.enums import HeroClass, HeroGeneration, Rarity
from src.schemas.exclusive_gear import (
    HeroExclusiveGearProgressionResponse,
    HeroExclusiveGearResponse,
)
from src.schemas.hero import HeroBasicResponse, HeroListResponse
from src.schemas.skills import HeroSkillResponse
from src.schemas.stats import (
    ConquestStatsResponse,
    ExpeditionStatsResponse,
    HeroStatsBundleResponse,
)
from src.schemas.talent import HeroTalentResponse

router = APIRouter(prefix="/heroes", tags=["heroes"])


@router.get("/", response_model=HeroListResponse)
def list_heroes(
    generation: Optional[HeroGeneration] = Query(
        None, description="Filter by generation (1, 2, or 3)"
    ),
    rarity: Optional[Rarity] = Query(
        None, description="Filter by rarity (Rare, Epic, Mythic)"
    ),
    hero_class: Optional[HeroClass] = Query(
        None, alias="class", description="Filter by class (Infantry, Cavalry, Archer)"
    ),
    limit: int = Query(
        50,
        ge=1,
        le=100,
        description="Maximum number of heroes to return (max 100)",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of heroes to skip before collecting results",
    ),
    hero_repo: HeroRepository = Depends(get_hero_repository),
) -> HeroListResponse:
    """List all heroes with optional filters.

    Query parameters:
    - generation: Filter by hero generation (1, 2, or 3)
    - rarity: Filter by rarity (Rare, Epic, Mythic)
    - class: Filter by hero class (Infantry, Cavalry, Archer)
    - limit: Maximum number of heroes returned (default 50, max 100)
    - offset: Pagination cursor for the next batch of heroes

    Returns a list of heroes matching the filters.
    """
    heroes, total = hero_repo.list_filtered(
        generation=generation.value if generation else None,
        rarity=rarity.value if rarity else None,
        hero_class=hero_class.value if hero_class else None,
        limit=limit,
        offset=offset,
    )

    return HeroListResponse(heroes=heroes, total=total)


@router.get("/{hero_slug}", response_model=HeroBasicResponse)
def get_hero(
    hero_slug: str,
    hero_repo: HeroRepository = Depends(get_hero_repository),
) -> HeroBasicResponse:
    """Get a single hero by their ID.

    Args:
        hero_slug: The hero's unique identifier (e.g., 'jabel', 'olive')

    Returns:
        Hero details

    Raises:
        404: If hero not found
    """
    hero = hero_repo.get_by_slug(hero_slug)

    if not hero:
        raise HTTPException(status_code=404, detail=f"Hero '{hero_slug}' not found")

    return hero


async def _hero_or_404(hero_slug: str, hero_repo: HeroRepository) -> HeroBasicResponse:
    hero = await run_in_threadpool(hero_repo.get_by_slug, hero_slug)
    if hero is None:
        raise HTTPException(status_code=404, detail=f"Hero '{hero_slug}' not found")
    return hero


@router.get(
    "/{hero_slug}/skills",
    response_model=List[HeroSkillResponse],
    summary="List skills for a specific hero",
)
async def get_hero_skills(
    hero_slug: str,
    hero_repo: HeroRepository = Depends(get_hero_repository),
    skills_repo: SkillsRepository = Depends(get_skills_repository),
) -> List[HeroSkillResponse]:
    hero = await _hero_or_404(hero_slug, hero_repo)
    skills = await run_in_threadpool(skills_repo.list_by_hero, str(hero.id))
    return skills


@router.get(
    "/{hero_slug}/exclusive-gear",
    response_model=List[HeroExclusiveGearResponse],
    summary="List exclusive gear for a specific hero",
)
async def get_hero_exclusive_gear(
    hero_slug: str,
    hero_repo: HeroRepository = Depends(get_hero_repository),
    gear_repo: ExclusiveGearRepository = Depends(get_exclusive_gear_repository),
) -> List[HeroExclusiveGearResponse]:
    await _hero_or_404(hero_slug, hero_repo)
    gear = await run_in_threadpool(gear_repo.list_by_hero_slug, hero_slug)
    return gear


@router.get(
    "/{hero_slug}/talents",
    response_model=List[HeroTalentResponse],
    summary="List hero talents",
)
async def get_hero_talents(
    hero_slug: str,
    hero_repo: HeroRepository = Depends(get_hero_repository),
    talent_repo: TalentRepository = Depends(get_talent_repository),
) -> List[HeroTalentResponse]:
    await _hero_or_404(hero_slug, hero_repo)
    talents = await run_in_threadpool(talent_repo.list_by_hero_slug, hero_slug)
    return talents


@router.get(
    "/{hero_slug}/exclusive-gear/progression",
    response_model=HeroExclusiveGearProgressionResponse,
    summary="Get exclusive gear progression details",
)
async def get_hero_exclusive_gear_progression(
    hero_slug: str,
    hero_repo: HeroRepository = Depends(get_hero_repository),
    gear_repo: ExclusiveGearRepository = Depends(get_exclusive_gear_repository),
) -> HeroExclusiveGearProgressionResponse:
    await _hero_or_404(hero_slug, hero_repo)
    progression = await run_in_threadpool(gear_repo.get_progression, hero_slug)
    if not progression:
        raise HTTPException(
            status_code=404,
            detail=f"No exclusive gear progression data for hero '{hero_slug}'",
        )
    return HeroExclusiveGearProgressionResponse(**progression)


@router.get(
    "/{hero_slug}/stats",
    response_model=HeroStatsBundleResponse,
    summary="Get both conquest and expedition stats for a hero",
)
async def get_hero_stats(
    hero_slug: str,
    hero_repo: HeroRepository = Depends(get_hero_repository),
    conquest_repo: HeroConquestStatsRepository = Depends(get_conquest_stats_repository),
    expedition_repo: HeroExpeditionStatsRepository = Depends(
        get_expedition_stats_repository
    ),
) -> HeroStatsBundleResponse:
    hero = await _hero_or_404(hero_slug, hero_repo)
    conquest = await run_in_threadpool(conquest_repo.list_by_hero_slug, hero_slug)
    expedition = await run_in_threadpool(expedition_repo.list_by_hero_slug, hero_slug)
    return HeroStatsBundleResponse(
        hero_id=hero.id,
        hero_slug=hero.hero_id_slug,
        hero_name=hero.name,
        conquest=conquest,
        expedition=expedition,
    )


@router.get(
    "/{hero_slug}/stats/conquest",
    response_model=List[ConquestStatsResponse],
    summary="Get conquest stats for a hero",
)
async def get_hero_conquest_stats(
    hero_slug: str,
    hero_repo: HeroRepository = Depends(get_hero_repository),
    conquest_repo: HeroConquestStatsRepository = Depends(get_conquest_stats_repository),
) -> List[ConquestStatsResponse]:
    await _hero_or_404(hero_slug, hero_repo)
    stats = await run_in_threadpool(conquest_repo.list_by_hero_slug, hero_slug)
    return stats


@router.get(
    "/{hero_slug}/stats/expedition",
    response_model=List[ExpeditionStatsResponse],
    summary="Get expedition stats for a hero",
)
async def get_hero_expedition_stats(
    hero_slug: str,
    hero_repo: HeroRepository = Depends(get_hero_repository),
    expedition_repo: HeroExpeditionStatsRepository = Depends(
        get_expedition_stats_repository
    ),
) -> List[ExpeditionStatsResponse]:
    await _hero_or_404(hero_slug, hero_repo)
    stats = await run_in_threadpool(expedition_repo.list_by_hero_slug, hero_slug)
    return stats
