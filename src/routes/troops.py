"""Troops endpoints with RESTful design.

Provides:
- GET /troops - List all troops with flexible filtering
- GET /troops/{troop_type}/{troop_level} - Get specific troop configuration
"""

from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.db.repositories.troops import TroopsRepository
from src.dependencies import get_troops_repository
from src.schemas.troops import (
    GroupBy,
    Troop,
    TroopsGroupedByType,
    TroopStats,
    TroopType,
)

router = APIRouter(prefix="/troops", tags=["troops"])


@router.get("/", response_model=Union[TroopsGroupedByType, List[Troop]])
def get_all_troops(
    type: Optional[TroopType] = Query(None, description="Filter by troop type"),
    level: Optional[int] = Query(None, ge=1, le=11, description="Exact troop level"),
    min_level: Optional[int] = Query(
        None, ge=1, le=11, description="Minimum troop level"
    ),
    max_level: Optional[int] = Query(
        None, ge=1, le=11, description="Maximum troop level"
    ),
    tg: Optional[int] = Query(None, ge=0, le=10, description="Exact True Gold level"),
    min_tg: Optional[int] = Query(
        None, ge=0, le=10, description="Minimum True Gold level"
    ),
    max_tg: Optional[int] = Query(
        None, ge=0, le=10, description="Maximum True Gold level"
    ),
    group_by: Optional[GroupBy] = Query(
        None, description="Group by 'type' (default) or 'none' for flat list"
    ),
    repo: TroopsRepository = Depends(get_troops_repository),
) -> Union[TroopsGroupedByType, List[Troop]]:
    """Get troops with flexible filtering.

    Provides complete troop stat data for consumption by external tools.

    Supports both exact matches and range queries:
    - Exact: ?type=infantry&level=11&tg=5
    - Range: ?min_level=8&max_level=10&min_tg=0&max_tg=5

    By default, returns troops grouped by type for easier consumption.
    Use group_by=none for a flat list.

    Args:
        type: Filter by Infantry, Cavalry, or Archer
        level: Exact troop level (overrides min/max_level)
        min_level: Minimum troop level (default 1 if no level specified)
        max_level: Maximum troop level (default 10 if no level specified)
        tg: Exact True Gold level (overrides min/max_tg)
        min_tg: Minimum True Gold level (default 0 if no tg specified)
        max_tg: Maximum True Gold level (default 5 if no tg specified)
        group_by: Return grouped by type (default) or flat list

    Returns:
        Grouped dict or flat list of troop configurations matching filters
    """
    # Handle exact match vs range queries
    final_min_level = (
        level if level is not None else (min_level if min_level is not None else 1)
    )
    final_max_level = (
        level if level is not None else (max_level if max_level is not None else 10)
    )
    final_min_tg = tg if tg is not None else (min_tg if min_tg is not None else 0)
    final_max_tg = tg if tg is not None else (max_tg if max_tg is not None else 5)

    troops = repo.get_all(
        troop_type=type,
        min_level=final_min_level,
        max_level=final_max_level,
        min_tg=final_min_tg,
        max_tg=final_max_tg,
    )

    # Return flat list if explicitly requested OR if filtering by specific type
    # (no point grouping when there's only one type)
    if (group_by is not None and group_by == GroupBy.none) or type is not None:
        return troops

    # Group by type (default behavior when querying all types)
    grouped: TroopsGroupedByType = TroopsGroupedByType()

    for troop in troops:
        troop_stats = TroopStats(
            troop_type=troop.troop_type,
            troop_level=troop.troop_level,
            true_gold_level=troop.true_gold_level,
            stats={
                "attack": troop.attack,
                "defense": troop.defense,
                "health": troop.health,
                "lethality": troop.lethality,
                "power": troop.power,
                "load": troop.load,
                "speed": troop.speed,
            },
            training=(
                {
                    "training_time_seconds": troop.training_time_seconds,
                    "training_power": troop.training_power,
                }
                if troop.training_time_seconds is not None
                and troop.training_power is not None
                else None
            ),
            costs=(
                troop.training_costs
                if troop.training_costs and len(troop.training_costs) > 0
                else None
            ),
            events=(
                troop.event_points
                if troop.event_points and len(troop.event_points) > 0
                else None
            ),
        )

        if troop.troop_type == TroopType.infantry:
            grouped.Infantry.append(troop_stats)
        elif troop.troop_type == TroopType.cavalry:
            grouped.Cavalry.append(troop_stats)
        elif troop.troop_type == TroopType.archer:
            grouped.Archer.append(troop_stats)

    return grouped


@router.get("/{troop_type}/{troop_level}", response_model=Troop)
def get_troop_by_configuration(
    troop_type: TroopType = Path(..., description="Troop type"),
    troop_level: int = Path(..., ge=1, le=11, description="Troop level"),
    true_gold_level: int = Query(0, ge=0, le=10, description="True Gold level"),
    repo: TroopsRepository = Depends(get_troops_repository),
) -> Troop:
    """Get specific troop configuration data.

    Args:
        troop_type: Infantry, Cavalry, or Archer
        troop_level: Troop level (1-11)
        true_gold_level: True Gold tier (0-10, default 0)

    Returns:
        Complete troop stat data for the specified configuration

    Raises:
        HTTPException: 404 if configuration not found
    """
    troop = repo.get_by_configuration(
        troop_type=troop_type,
        troop_level=troop_level,
        true_gold_level=true_gold_level,
    )

    if not troop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{troop_type.value} level {troop_level} TG{true_gold_level} not found",
        )

    return troop
