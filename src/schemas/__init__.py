"""Schemas package - API request/response schemas for the Heroes API."""

from .exclusive_gear import (
    HeroExclusiveGearCreateRequest,
    HeroExclusiveGearLevelCreateRequest,
    HeroExclusiveGearLevelResponse,
    HeroExclusiveGearResponse,
    HeroExclusiveGearSkillCreateRequest,
    HeroExclusiveGearSkillResponse,
)
from .hero import (
    HeroBasicResponse,
    HeroCreateRequest,
    HeroDetailResponse,
    HeroListResponse,
    HeroUpdateRequest,
)
from .skills import (
    HeroSkillCreateRequest,
    HeroSkillLevelCreateRequest,
    HeroSkillLevelResponse,
    HeroSkillListResponse,
    HeroSkillResponse,
)
from .stats import (
    HeroExpeditionStatsCreateRequest,
    HeroExpeditionStatsListResponse,
    HeroExpeditionStatsResponse,
    HeroStatsBundleResponse,
    HeroStatsCreateRequest,
    HeroStatsListResponse,
    HeroStatsResponse,
)
from .talent import HeroTalentCreateRequest, HeroTalentListResponse, HeroTalentResponse
from .troops import (
    GroupBy,
    Troop,
    TroopBase,
    TroopCreate,
    TroopFilter,
    TroopsGroupedByType,
    TroopStats,
    TroopType,
)
from .vip import VIPLevel, VIPLevelBase

__all__ = [
    # Hero
    "HeroBasicResponse",
    "HeroListResponse",
    "HeroDetailResponse",
    "HeroCreateRequest",
    "HeroUpdateRequest",
    # Stats
    "HeroStatsResponse",
    "HeroExpeditionStatsResponse",
    "HeroStatsCreateRequest",
    "HeroExpeditionStatsCreateRequest",
    "HeroStatsListResponse",
    "HeroExpeditionStatsListResponse",
    "HeroStatsBundleResponse",
    # Skills
    "HeroSkillResponse",
    "HeroSkillLevelResponse",
    "HeroSkillCreateRequest",
    "HeroSkillLevelCreateRequest",
    "HeroSkillListResponse",
    # Exclusive Gear
    "HeroExclusiveGearResponse",
    "HeroExclusiveGearLevelResponse",
    "HeroExclusiveGearSkillResponse",
    "HeroExclusiveGearCreateRequest",
    "HeroExclusiveGearLevelCreateRequest",
    "HeroExclusiveGearSkillCreateRequest",
    # Talents
    "HeroTalentResponse",
    "HeroTalentCreateRequest",
    "HeroTalentListResponse",
    # VIP
    "VIPLevel",
    "VIPLevelBase",
    # Troops
    "Troop",
    "TroopBase",
    "TroopCreate",
    "TroopFilter",
    "TroopType",
    "TroopStats",
    "TroopsGroupedByType",
    "GroupBy",
]
