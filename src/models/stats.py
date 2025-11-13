"""Hero stats database models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HeroStatsBase(BaseModel):
    """Base hero conquest stats model."""

    model_config = ConfigDict(from_attributes=True)

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    attack: int = Field(..., ge=0, description="Attack stat")
    defense: int = Field(..., ge=0, description="Defense stat")
    health: int = Field(..., ge=0, description="Health stat")


class HeroStatsCreate(HeroStatsBase):
    """Model for creating hero conquest stats."""

    pass


class HeroStats(HeroStatsBase):
    """Complete hero conquest stats model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HeroExpeditionStatsBase(BaseModel):
    """Base hero expedition stats model."""

    model_config = ConfigDict(from_attributes=True)

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    troop_type: str = Field(
        ..., description="Troop type the expedition bonuses apply to"
    )
    attack_pct: Optional[Decimal] = Field(
        None, description="Attack percentage bonus for the specified troop type"
    )
    defense_pct: Optional[Decimal] = Field(
        None, description="Defense percentage bonus for the specified troop type"
    )


class HeroExpeditionStatsCreate(HeroExpeditionStatsBase):
    """Model for creating hero expedition stats."""

    pass


class HeroExpeditionStats(HeroExpeditionStatsBase):
    """Complete hero expedition stats model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
