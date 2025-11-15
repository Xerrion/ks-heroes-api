"""Governor Gear Pydantic schemas"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.schemas.enums import GearRarity, HeroClass


class GovernorGearBase(BaseModel):
    """Base governor gear piece schema"""

    gear_id: str = Field(
        ...,
        description="Unique gear identifier (head, amulet, chest, legs, ring, staff)",
    )
    slot: str = Field(..., description="Display name for equipment slot")
    troop_type: HeroClass = Field(
        ..., description="Troop type this gear benefits (Infantry, Cavalry, Archer)"
    )
    max_charms: int = Field(
        default=3, ge=1, description="Maximum charm slots available"
    )
    description: Optional[str] = Field(None, description="Gear description")
    default_bonus_keys: List[str] = Field(
        default_factory=list,
        description="Default bonus stat keys (e.g., ['attack_pct', 'defense_pct'])",
    )


class GovernorGear(GovernorGearBase):
    """Governor gear piece with metadata for API responses"""

    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gear_id": "head",
                "slot": "Head",
                "troop_type": "Cavalry",
                "max_charms": 3,
                "description": "Governor head gear - provides Cavalry bonuses",
                "default_bonus_keys": ["attack_pct", "defense_pct"],
            }
        }


class GovernorGearLevelBase(BaseModel):
    """Base governor gear level schema"""

    level: int = Field(
        ..., ge=1, le=46, description="Absolute progression level (1-46)"
    )
    rarity: GearRarity = Field(
        ..., description="Gear rarity (Uncommon, Rare, Epic, Mythic, Legendary)"
    )
    tier: int = Field(
        ...,
        ge=0,
        le=4,
        description="Tier within rarity (0-4, higher tiers available at higher rarities)",
    )
    stars: int = Field(..., ge=0, le=5, description="Star level within tier (0-5)")
    name: Optional[str] = Field(
        None,
        description="Display name for gear at this rarity (same across all tiers/stars)",
    )
    bonuses: Dict[str, Any] = Field(
        default_factory=dict,
        description="Combat stat bonuses as object (e.g., {'attack_pct': 34.0, 'defense_pct': 34.0})",
    )


class GovernorGearLevel(GovernorGearLevelBase):
    """Governor gear level with metadata for API responses"""

    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "level": 7,
                "rarity": "Epic",
                "tier": 0,
                "stars": 0,
                "name": "Regal Headdress",
                "bonuses": {"attack_pct": 34.0, "defense_pct": 34.0},
            }
        }


class GovernorGearCharmSlotBase(BaseModel):
    """Base governor gear charm slot schema"""

    gear_id: str = Field(
        ..., description="Reference to governor_gear piece (head, amulet, etc.)"
    )
    slot_index: int = Field(..., ge=1, le=3, description="Slot position (1-3)")
    troop_type: HeroClass = Field(
        ..., description="Troop type for this slot (inherited from gear)"
    )
    bonus_keys: List[str] = Field(
        default_factory=list,
        description="Stat keys provided by charms in this slot (e.g., ['troop_lethality_pct', 'troop_health_pct'])",
    )


class GovernorGearCharmSlot(GovernorGearCharmSlotBase):
    """Governor gear charm slot with metadata for API responses"""

    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "gear_id": "head",
                "slot_index": 1,
                "troop_type": "Cavalry",
                "bonus_keys": ["troop_lethality_pct", "troop_health_pct"],
            }
        }


class GovernorGearCharmLevelBase(BaseModel):
    """Base governor gear charm level schema"""

    level: int = Field(..., ge=1, le=16, description="Charm level (1-16)")
    bonuses: Dict[str, Any] = Field(
        default_factory=dict,
        description="Combat stat bonuses as object (e.g., {'troop_lethality_pct': 9.0, 'troop_health_pct': 9.0})",
    )


class GovernorGearCharmLevel(GovernorGearCharmLevelBase):
    """Governor gear charm level with metadata for API responses"""

    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "level": 1,
                "bonuses": {"troop_lethality_pct": 9.0, "troop_health_pct": 9.0},
            }
        }


class GovernorGearWithCharms(GovernorGear):
    """Governor gear piece with charm slot information"""

    charm_slots: List[GovernorGearCharmSlot] = Field(
        default_factory=list, description="Available charm slots for this gear piece"
    )

    class Config(GovernorGear.Config):
        json_schema_extra = {
            "example": {
                "gear_id": "head",
                "slot": "Head",
                "troop_type": "Cavalry",
                "max_charms": 3,
                "description": "Governor head gear - provides Cavalry bonuses",
                "default_bonus_keys": ["attack_pct", "defense_pct"],
                "charm_slots": [
                    {
                        "id": 1,
                        "gear_id": "head",
                        "slot_index": 1,
                        "troop_type": "Cavalry",
                        "bonus_keys": ["troop_lethality_pct", "troop_health_pct"],
                    }
                ],
            }
        }


class GovernorGearFilter(BaseModel):
    """Schema for filtering governor gear in queries"""

    troop_type: Optional[HeroClass] = Field(
        None, description="Filter by troop type (Infantry, Cavalry, Archer)"
    )
    rarity: Optional[GearRarity] = Field(
        None, description="Filter by rarity (Uncommon, Rare, Epic, Mythic, Legendary)"
    )
    min_level: int = Field(1, ge=1, le=46, description="Minimum gear level")
    max_level: int = Field(46, ge=1, le=46, description="Maximum gear level")

    class Config:
        json_schema_extra = {
            "example": {
                "troop_type": "Cavalry",
                "rarity": "Epic",
                "min_level": 1,
                "max_level": 46,
            }
        }
