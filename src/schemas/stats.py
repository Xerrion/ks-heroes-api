"""Hero stats API schemas."""

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class HeroStatsResponse(BaseModel):
    """Response model for hero conquest stats."""

    id: UUID = Field(..., description="Database primary key")
    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    attack: int = Field(..., description="Attack stat")
    defense: int = Field(..., description="Defense stat")
    health: int = Field(..., description="Health stat")

    class Config:
        from_attributes = True


class HeroExpeditionStatsResponse(BaseModel):
    """Response model for hero expedition stats."""

    id: UUID = Field(..., description="Database primary key")
    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    troop_type: str = Field(..., description="Troop type boosted by this hero")
    attack_pct: Optional[Decimal] = Field(
        None, description="Attack percentage bonus for the troop type"
    )
    defense_pct: Optional[Decimal] = Field(
        None, description="Defense percentage bonus for the troop type"
    )

    class Config:
        from_attributes = True


class HeroStatsBundleResponse(BaseModel):
    """Response containing both conquest and expedition stats for a hero."""

    hero_id: UUID = Field(..., description="Hero identifier")
    hero_slug: str = Field(..., description="Hero slug")
    hero_name: Optional[str] = Field(None, description="Hero name")
    conquest: List[HeroStatsResponse] = Field(
        default_factory=list, description="Conquest stat entries"
    )
    expedition: List[HeroExpeditionStatsResponse] = Field(
        default_factory=list, description="Expedition stat entries"
    )

    class Config:
        from_attributes = True


class HeroStatsCreateRequest(BaseModel):
    """Request model for creating hero conquest stats."""

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    attack: int = Field(..., ge=0, description="Attack stat")
    defense: int = Field(..., ge=0, description="Defense stat")
    health: int = Field(..., ge=0, description="Health stat")

    class Config:
        from_attributes = True


class HeroExpeditionStatsCreateRequest(BaseModel):
    """Request model for creating hero expedition stats."""

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    troop_type: str = Field(..., description="Troop type boosted by this hero")
    attack_pct: Optional[Decimal] = Field(
        None, description="Attack percentage bonus for the troop type"
    )
    defense_pct: Optional[Decimal] = Field(
        None, description="Defense percentage bonus for the troop type"
    )

    class Config:
        from_attributes = True


class HeroStatsListResponse(BaseModel):
    """Response for list of hero conquest stats."""

    stats: List[HeroStatsResponse]
    total: int

    class Config:
        from_attributes = True


class HeroExpeditionStatsListResponse(BaseModel):
    """Response for list of hero expedition stats."""

    stats: List[HeroExpeditionStatsResponse]
    total: int

    class Config:
        from_attributes = True
