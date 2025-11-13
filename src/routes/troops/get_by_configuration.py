"""Get specific troop configuration endpoint."""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.db.repositories.troops import TroopsRepository
from src.dependencies import get_troops_repository
from src.schemas.troops import Troop, TroopType

router = APIRouter()


@router.get("/{troop_type}/{troop_level}", response_model=Troop)
async def get_troop_by_configuration(
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
    troop = await repo.get_by_configuration(
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
