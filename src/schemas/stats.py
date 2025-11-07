"""Hero stats API schemas."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class HeroStatsResponse(BaseModel):
    """Response model for hero conquest stats."""

    id: UUID = Field(..., description="Database primary key")
    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    level: int = Field(..., description="Hero level")
    attack: int = Field(..., description="Attack stat")
    defense: int = Field(..., description="Defense stat")
    health: int = Field(..., description="Health stat")
    power: int = Field(..., description="Total power")

    class Config:
        from_attributes = True


class HeroExpeditionStatsResponse(BaseModel):
    """Response model for hero expedition stats."""

    id: UUID = Field(..., description="Database primary key")
    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    level: int = Field(..., description="Hero level")
    attack: int = Field(..., description="Attack stat")
    defense: int = Field(..., description="Defense stat")
    health: int = Field(..., description="Health stat")

    class Config:
        from_attributes = True


class HeroStatsCreateRequest(BaseModel):
    """Request model for creating hero conquest stats."""

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    level: int = Field(..., ge=1, description="Hero level")
    attack: int = Field(..., ge=0, description="Attack stat")
    defense: int = Field(..., ge=0, description="Defense stat")
    health: int = Field(..., ge=0, description="Health stat")
    power: int = Field(..., ge=0, description="Total power")

    class Config:
        from_attributes = True


class HeroExpeditionStatsCreateRequest(BaseModel):
    """Request model for creating hero expedition stats."""

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    level: int = Field(..., ge=1, description="Hero level")
    attack: int = Field(..., ge=0, description="Attack stat")
    defense: int = Field(..., ge=0, description="Defense stat")
    health: int = Field(..., ge=0, description="Health stat")

    class Config:
        from_attributes = True


class HeroStatsListResponse(BaseModel):
    """Response for list of hero stats."""

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
