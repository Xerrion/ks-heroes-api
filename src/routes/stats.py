"""Stats endpoints with RESTful design.

Provides:
- GET /stats/conquest - List all conquest stats with optional hero filter
- GET /stats/expedition - List all expedition stats with optional hero filter
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from src.db.repositories.stats import StatsRepository
from src.dependencies import get_stats_repository
from src.schemas.stats import ConquestStatsResponse, ExpeditionStatsResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/conquest", response_model=List[ConquestStatsResponse])
def list_conquest_stats(
    hero: Optional[str] = Query(
        None, description="Filter by hero ID (e.g., 'jabel', 'olive')"
    ),
    stats_repo: StatsRepository = Depends(get_stats_repository),
) -> List[ConquestStatsResponse]:
    """List all hero conquest stats.

    Query parameters:
    - hero: Filter by hero ID (e.g., 'jabel', 'olive')

    Returns a list of conquest stats (attack, defense, health).
    Note: Conquest stats have no level progression in the current data.
    """
    if hero:
        stats = stats_repo.list_conquest_by_hero_slug(hero)
    else:
        stats = stats_repo.list_all_conquest()

    return [ConquestStatsResponse(**stat) for stat in stats]


@router.get("/expedition", response_model=List[ExpeditionStatsResponse])
def list_expedition_stats(
    hero: Optional[str] = Query(
        None, description="Filter by hero ID (e.g., 'jabel', 'olive')"
    ),
    stats_repo: StatsRepository = Depends(get_stats_repository),
) -> List[ExpeditionStatsResponse]:
    """List all hero expedition stats.

    Query parameters:
    - hero: Filter by hero ID (e.g., 'jabel', 'olive')

    Returns a list of expedition stats (percentage bonuses by troop type).
    Each hero typically has three entries (Infantry, Cavalry, Archer bonuses).
    """
    if hero:
        stats = stats_repo.list_expedition_by_hero_slug(hero)
    else:
        stats = stats_repo.list_all_expedition()

    return [ExpeditionStatsResponse(**stat) for stat in stats]
