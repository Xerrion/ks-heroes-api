"""VIP Level Pydantic schemas"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class VIPLevelBase(BaseModel):
    """Base VIP level schema with all attributes"""

    level: int = Field(..., ge=1, le=12, description="VIP level (1-12)")

    # Resource production
    resource_production_speed_pct: Decimal = Field(
        default=Decimal("0.0"),
        ge=0,
        description="Resource production speed bonus - applies to Bread/Wood/Stone/Iron Output (Percentage)",
    )

    # Storage
    storehouse_capacity: int = Field(
        default=0, ge=0, description="Storehouse capacity increase (flat number)"
    )

    # Speed bonuses
    construction_speed_pct: Decimal = Field(
        default=Decimal("0.0"), ge=0, description="Construction Speed (Percentage)"
    )

    # Gameplay features (counts)
    formations: int = Field(
        default=0, ge=0, description="Number of formation slots available"
    )

    march_queue: int = Field(
        default=0,
        ge=0,
        description="March Queue - number of concurrent marches allowed",
    )

    # Combat bonuses (all troops)
    squads_attack_pct: Decimal = Field(
        default=Decimal("0.0"),
        ge=0,
        description="Squads' Attack (Percentage) - applies to all troop types",
    )

    squads_defense_pct: Decimal = Field(
        default=Decimal("0.0"),
        ge=0,
        description="Squads' Defense (Percentage) - applies to all troop types",
    )

    squads_health_pct: Decimal = Field(
        default=Decimal("0.0"),
        ge=0,
        description="Squads' Health (Percentage) - applies to all troop types",
    )

    squads_lethality_pct: Decimal = Field(
        default=Decimal("0.0"),
        ge=0,
        description="Squads' Lethality (Percentage) - applies to all troop types",
    )

    # Cosmetic
    custom_avatar_upload_cooldown_hours: int = Field(
        default=0,
        description="Avatar upload cooldown modification. Negative values indicate reduction (e.g., -48 = 48 hours less cooldown)",
    )


class VIPLevel(VIPLevelBase):
    """VIP level schema with metadata for API responses"""

    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "level": 12,
                "resource_production_speed_pct": 24.0,
                "storehouse_capacity": 1100000,
                "construction_speed_pct": 20.0,
                "formations": 2,
                "march_queue": 1,
                "squads_attack_pct": 16.0,
                "squads_defense_pct": 16.0,
                "squads_health_pct": 16.0,
                "squads_lethality_pct": 16.0,
                "custom_avatar_upload_cooldown_hours": -48,
            }
        }
