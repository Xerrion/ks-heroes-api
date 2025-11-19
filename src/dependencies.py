"""Shared FastAPI dependencies for the KS-Heroes API."""

from fastapi import Depends, HTTPException

from src.db.repositories.exclusive_gear import ExclusiveGearRepository
from src.db.repositories.governor_gear import GovernorGearRepository
from src.db.repositories.hero import HeroRepository
from src.db.repositories.skills import SkillsRepository
from src.db.repositories.stats import (
    HeroConquestStatsRepository,
    HeroExpeditionStatsRepository,
)
from src.db.repositories.talent import TalentRepository
from src.db.repositories.troops import TroopsRepository
from src.db.repositories.vip import VIPRepository
from src.db.supabase_client import SupabaseClientError
from src.db.supabase_client import get_supabase_client as _get_supabase_client
from supabase import Client


def get_supabase_client() -> Client:
    """Return the Supabase client instance ready for injection."""

    try:
        client = _get_supabase_client()
    except (
        SupabaseClientError,
        RuntimeError,
    ) as exc:  # pragma: no cover - env specific
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured or unavailable.",
        ) from exc

    return client


def get_vip_repository(
    supabase: Client = Depends(get_supabase_client),
) -> VIPRepository:
    """Dependency injection for VIP repository."""
    return VIPRepository(supabase)


def get_troops_repository(
    supabase: Client = Depends(get_supabase_client),
) -> TroopsRepository:
    """Dependency injection for Troops repository."""
    return TroopsRepository(supabase)


def get_hero_repository(
    supabase: Client = Depends(get_supabase_client),
) -> HeroRepository:
    """Dependency injection for Hero repository."""
    return HeroRepository(supabase)


def get_skills_repository(
    supabase: Client = Depends(get_supabase_client),
) -> SkillsRepository:
    """Dependency injection for Skills repository."""
    return SkillsRepository(supabase)


def get_conquest_stats_repository(
    supabase: Client = Depends(get_supabase_client),
) -> HeroConquestStatsRepository:
    """Dependency injection for conquest stats repository."""
    return HeroConquestStatsRepository(supabase)


def get_expedition_stats_repository(
    supabase: Client = Depends(get_supabase_client),
) -> HeroExpeditionStatsRepository:
    """Dependency injection for expedition stats repository."""
    return HeroExpeditionStatsRepository(supabase)


def get_talent_repository(
    supabase: Client = Depends(get_supabase_client),
) -> TalentRepository:
    """Dependency injection for Talent repository."""
    return TalentRepository(supabase)


def get_exclusive_gear_repository(
    supabase: Client = Depends(get_supabase_client),
) -> ExclusiveGearRepository:
    """Dependency injection for Exclusive Gear repository."""
    return ExclusiveGearRepository(supabase)


def get_governor_gear_repository(
    supabase: Client = Depends(get_supabase_client),
) -> GovernorGearRepository:
    """Dependency injection for Governor Gear repository."""
    return GovernorGearRepository(supabase)
