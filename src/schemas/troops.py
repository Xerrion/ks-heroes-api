"""Troop Pydantic schemas"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TroopType(str, Enum):
    """Troop type enum matching hero_class database enum"""

    infantry = "Infantry"
    cavalry = "Cavalry"
    archer = "Archer"


class TroopBase(BaseModel):
    """Base troop schema with all attributes"""

    troop_type: TroopType = Field(..., description="Infantry, Cavalry, or Archer")
    troop_level: int = Field(
        ..., ge=1, le=11, description="Troop level (1-10 regular, 11 is Helios)"
    )
    true_gold_level: int = Field(
        default=0,
        ge=0,
        le=10,
        description="True Gold level (0 = no TG bonuses, 1-10 = TG tiers)",
    )

    # Base combat stats (flat numbers)
    attack: int = Field(..., ge=0, description="Base attack value (flat number)")
    defense: int = Field(..., ge=0, description="Base defense value (flat number)")
    health: int = Field(..., ge=0, description="Base health value (flat number)")
    lethality: int = Field(..., ge=0, description="Base lethality value (flat number)")

    # Other base stats
    power: int = Field(
        ..., ge=0, description="Troop power - used for overall power calculations"
    )
    load: int = Field(..., ge=0, description="Resource carrying capacity per troop")
    speed: int = Field(..., ge=0, description="March speed on the map")


class Troop(TroopBase):
    """Troop schema with metadata for API responses"""

    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "troop_type": "Cavalry",
                "troop_level": 10,
                "true_gold_level": 5,
                "attack": 20,
                "defense": 26,
                "health": 30,
                "lethality": 20,
                "power": 132,
                "load": 758,
                "speed": 14,
            }
        }


class TroopCreate(TroopBase):
    """Schema for creating a new troop configuration"""

    pass


class TroopFilter(BaseModel):
    """Schema for filtering troops in queries"""

    troop_type: Optional[TroopType] = Field(None, description="Filter by troop type")
    min_level: int = Field(1, ge=1, le=11, description="Minimum troop level")
    max_level: int = Field(
        10, ge=1, le=11, description="Maximum troop level (default excludes Helios)"
    )
    min_tg: int = Field(0, ge=0, le=10, description="Minimum True Gold level")
    max_tg: int = Field(
        5, ge=0, le=10, description="Maximum True Gold level (default for current game)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "troop_type": "Infantry",
                "min_level": 1,
                "max_level": 10,
                "min_tg": 0,
                "max_tg": 5,
            }
        }
