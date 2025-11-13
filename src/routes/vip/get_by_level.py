"""Get specific VIP level endpoint."""

from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.db.repositories.vip import VIPRepository
from src.dependencies import get_vip_repository
from src.schemas.vip import VIPLevel

router = APIRouter()


@router.get("/{level}", response_model=VIPLevel)
async def get_vip_level(
    level: int = Path(..., ge=1, le=12, description="VIP level"),
    repo: VIPRepository = Depends(get_vip_repository),
) -> VIPLevel:
    """Get specific VIP level bonus data.

    Args:
        level: VIP level (1-12)

    Returns:
        Complete VIP bonus data for the specified level

    Raises:
        HTTPException: 404 if VIP level not found
    """
    vip = await repo.get_by_level(level)

    if not vip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"VIP level {level} not found"
        )

    return vip
