"""Troop Pydantic schemas"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field

from src.db.storage import build_public_asset_url, resolve_asset_path


class TroopType(str, Enum):
    """Troop type enum matching hero_class database enum"""

    infantry = "Infantry"
    cavalry = "Cavalry"
    archer = "Archer"


class GroupBy(str, Enum):
    """Grouping options for troop responses"""

    type = "type"
    none = "none"


class TroopBase(BaseModel):
    """Base troop schema with all attributes"""

    troop_type: TroopType = Field(..., description="Infantry, Cavalry, or Archer")
    troop_level: int = Field(
        ..., ge=1, le=11, description="Troop level (1-10 regular, 11 is Helios)"
    )
    true_gold_level: int = Field(
        default=0,
        ge=0,
        le=5,
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

    # Training mechanics
    training_time_seconds: Optional[int] = Field(
        None, ge=0, description="Time to train one troop in seconds"
    )
    training_power: Optional[int] = Field(
        None, ge=0, description="Power gained from training one troop"
    )

    # Flat resource costs (for backward compatibility and simple access)
    bread: Optional[int] = Field(None, ge=0, description="Bread cost")
    wood: Optional[int] = Field(None, ge=0, description="Wood cost")
    stone: Optional[int] = Field(None, ge=0, description="Stone cost")
    iron: Optional[int] = Field(None, ge=0, description="Iron cost")

    # Flat event points (for backward compatibility and simple access)
    hog_event_points: Optional[int] = Field(
        None, ge=0, description="Hall of Glory points"
    )
    kvk_event_points: Optional[int] = Field(None, ge=0, description="KvK points")
    sg_event_points: Optional[int] = Field(
        None, ge=0, description="Server Glory points"
    )

    @computed_field
    @property
    def image_url(self) -> str | None:
        """Public URL for troop icon."""
        fallback_name = f"{self.troop_type.value.lower()}_{self.troop_level}"
        path = resolve_asset_path(folder="troops", fallback_name=fallback_name)
        return build_public_asset_url(path)

    # Related data (populated from joins)
    training_costs: Optional[Dict[str, int]] = Field(
        None, description="Resource costs per troop (bread, wood, stone, iron)"
    )
    event_points: Optional[Dict[str, int]] = Field(
        None, description="Event points per troop (hog, kvk, sg)"
    )


class Troop(TroopBase):
    """Troop schema with metadata for API responses"""

    id: int
    created_at: Optional[str] = Field(None, exclude=True)
    updated_at: Optional[str] = Field(None, exclude=True)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
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
                "image_url": "https://example.com/storage/v1/object/public/assets/troops/cavalry_10.png",
                "training_time_seconds": 152,
                "training_power": 66,
                "training_costs": {
                    "bread": 2440,
                    "wood": 2301,
                    "stone": 474,
                    "iron": 109,
                },
                "event_points": {"hog": 1960, "kvk": 60, "sg": 39},
            }
        },
    )


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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "troop_type": "Infantry",
                "min_level": 1,
                "max_level": 10,
                "min_tg": 0,
                "max_tg": 5,
            }
        }
    )


class TroopStats(BaseModel):
    """Troop stats without type information (for grouped responses)"""

    troop_type: Optional[TroopType] = Field(
        None, description="Infantry, Cavalry, or Archer"
    )
    troop_level: int = Field(
        ..., ge=1, le=11, description="Troop level (1-10 regular, 11 is Helios)"
    )
    true_gold_level: int = Field(
        ...,
        ge=0,
        le=10,
        description="True Gold level (0 = no TG bonuses, 1-10 = TG tiers)",
    )

    stats: Dict[str, int] = Field(
        ...,
        description="Combat and other stats (attack, defense, health, lethality, power, load, speed)",
    )

    @computed_field
    @property
    def image_url(self) -> str | None:
        """Public URL for troop icon."""
        if not self.troop_type:
            return None
        fallback_name = f"{self.troop_type.value.lower()}_{self.troop_level}"
        path = resolve_asset_path(folder="troops", fallback_name=fallback_name)
        return build_public_asset_url(path)

    training: Optional[Dict[str, int]] = Field(
        None,
        description="Training data (training_time_seconds, training_power)",
    )
    costs: Optional[Dict[str, int]] = Field(
        None,
        description="Resource costs (bread, wood, stone, iron)",
    )
    events: Optional[Dict[str, int]] = Field(
        None,
        description="Event points (hog, kvk, sg)",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "troop_type": "Infantry",
                "troop_level": 5,
                "true_gold_level": 2,
                "stats": {
                    "attack": 7,
                    "defense": 10,
                    "health": 12,
                    "lethality": 6,
                    "power": 15,
                    "load": 188,
                    "speed": 11,
                },
                "image_url": "https://example.com/storage/v1/object/public/assets/troops/infantry_5.png",
                "training": {
                    "training_time_seconds": 44,
                    "training_power": 13,
                },
                "costs": {
                    "bread": 136,
                    "wood": 129,
                    "stone": 27,
                    "iron": 7,
                },
                "events": {
                    "hog": 385,
                    "kvk": 12,
                    "sg": 7,
                },
            }
        },
    )


class TroopsGroupedByType(BaseModel):
    """Troops grouped by type (Infantry, Cavalry, Archer)"""

    Infantry: List[TroopStats] = Field(default_factory=list)
    Cavalry: List[TroopStats] = Field(default_factory=list)
    Archer: List[TroopStats] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Infantry": [
                    {
                        "troop_level": 5,
                        "true_gold_level": 2,
                        "stats": {
                            "attack": 7,
                            "defense": 10,
                            "health": 12,
                            "lethality": 6,
                            "power": 15,
                            "load": 188,
                            "speed": 11,
                        },
                    }
                ],
                "Cavalry": [],
                "Archer": [],
            }
        }
    )
