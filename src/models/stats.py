"""Hero stats database models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HeroStatsBase(BaseModel):
    """Base hero stats model."""

    model_config = ConfigDict(from_attributes=True)
    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    level: int = Field(..., ge=1, description="Hero level")
    attack: int = Field(..., ge=0, description="Attack stat")
    defense: int = Field(..., ge=0, description="Defense stat")
    health: int = Field(..., ge=0, description="Health stat")
    power: int = Field(..., ge=0, description="Total power")


class HeroStatsCreate(HeroStatsBase):
    """Model for creating hero stats."""

    pass


class HeroStats(HeroStatsBase):
    """Complete hero stats model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None


class HeroExpeditionStatsBase(BaseModel):
    """Base hero expedition stats model."""

    model_config = ConfigDict(from_attributes=True)

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    level: int = Field(..., ge=1, description="Hero level")
    attack: int = Field(..., ge=0, description="Attack stat")
    defense: int = Field(..., ge=0, description="Defense stat")
    health: int = Field(..., ge=0, description="Health stat")


class HeroExpeditionStatsCreate(HeroExpeditionStatsBase):
    """Model for creating hero expedition stats."""

    pass


class HeroExpeditionStats(HeroExpeditionStatsBase):
    """Complete hero expedition stats model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None
