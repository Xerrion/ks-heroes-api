"""Schemas package - API request/response schemas for the Heroes API."""
from .hero import (
    HeroBasicResponse,
    HeroListResponse,
    HeroDetailResponse,
    HeroCreateRequest,
    HeroUpdateRequest
)
from .stats import (
    HeroStatsResponse,
    HeroExpeditionStatsResponse,
    HeroStatsCreateRequest,
    HeroExpeditionStatsCreateRequest,
    HeroStatsListResponse,
    HeroExpeditionStatsListResponse
)
from .skills import (
    HeroSkillResponse,
    HeroSkillLevelResponse,
    HeroSkillCreateRequest,
    HeroSkillLevelCreateRequest,
    HeroSkillListResponse
)
from .exclusive_gear import (
    HeroExclusiveGearResponse,
    HeroExclusiveGearLevelResponse,
    HeroExclusiveGearSkillResponse,
    HeroExclusiveGearCreateRequest,
    HeroExclusiveGearLevelCreateRequest,
    HeroExclusiveGearSkillCreateRequest
)
from .talent import (
    HeroTalentResponse,
    HeroTalentCreateRequest,
    HeroTalentListResponse
)

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
]

