"""Stats endpoints with RESTful design.

Provides:
- GET /stats/conquest - List all conquest stats with optional hero filter
- GET /stats/expedition - List all expedition stats with optional hero filter
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.db.repositories.stats import (
    HeroConquestStatsRepository,
    HeroExpeditionStatsRepository,
)
from src.dependencies import (
    get_conquest_stats_repository,
    get_expedition_stats_repository,
)
from src.schemas.stats import HeroExpeditionStatsListResponse, HeroStatsListResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/conquest", response_model=HeroStatsListResponse)
def list_conquest_stats(
    hero: Optional[str] = Query(
        None, description="Filter by hero ID (e.g., 'jabel', 'olive')"
    ),
    limit: int = Query(
        50, ge=1, le=200, description="Maximum number of conquest stat rows to return"
    ),
    offset: int = Query(0, ge=0, description="Number of conquest stat rows to skip"),
    conquest_repo: HeroConquestStatsRepository = Depends(get_conquest_stats_repository),
) -> HeroStatsListResponse:
    """List all hero conquest stats.

    Query parameters:
    - hero: Filter by hero ID (e.g., 'jabel', 'olive')
    - limit/offset: Pagination controls

    Returns a list of conquest stats (attack, defense, health).
    Note: Conquest stats have no level progression in the current data.
    """
    stats, total = conquest_repo.list_filtered(
        hero_slug=hero,
        limit=limit,
        offset=offset,
    )
    return HeroStatsListResponse(stats=stats, total=total)


@router.get("/expedition", response_model=HeroExpeditionStatsListResponse)
def list_expedition_stats(
    hero: Optional[str] = Query(
        None, description="Filter by hero ID (e.g., 'jabel', 'olive')"
    ),
    limit: int = Query(
        50, ge=1, le=200, description="Maximum number of expedition stat rows to return"
    ),
    offset: int = Query(0, ge=0, description="Number of expedition stat rows to skip"),
    expedition_repo: HeroExpeditionStatsRepository = Depends(
        get_expedition_stats_repository
    ),
) -> HeroExpeditionStatsListResponse:
    """List all hero expedition stats.

    Query parameters:
    - hero: Filter by hero ID (e.g., 'jabel', 'olive')
    - limit/offset: Pagination controls

    Returns a list of expedition stats (percentage bonuses by troop type).
    Each hero typically has three entries (Infantry, Cavalry, Archer bonuses).
    """
    stats, total = expedition_repo.list_filtered(
        hero_slug=hero,
        limit=limit,
        offset=offset,
    )
    return HeroExpeditionStatsListResponse(stats=stats, total=total)
