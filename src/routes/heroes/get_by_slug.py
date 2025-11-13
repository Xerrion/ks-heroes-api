from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from src.db.repositories.exclusive_gear import ExclusiveGearRepository
from src.db.repositories.hero import HeroRepository
from src.db.repositories.skills import SkillsRepository
from src.db.repositories.stats import StatsRepository
from src.db.repositories.talent import TalentRepository
from src.dependencies import get_supabase_client
from src.schemas.exclusive_gear import HeroExclusiveGearResponse
from src.schemas.skills import HeroSkillResponse
from src.schemas.stats import (
    HeroExpeditionStatsResponse,
    HeroStatsBundleResponse,
    HeroStatsResponse,
)
from src.schemas.talent import HeroTalentResponse
from supabase import Client

router = APIRouter()


async def _hero_or_404(hero_slug: str, supabase: Client) -> Dict[str, Any]:
    repository = HeroRepository(supabase)
    hero = await run_in_threadpool(repository.get_by_slug, hero_slug)
    if hero is None:
        raise HTTPException(status_code=404, detail=f"Hero '{hero_slug}' not found")
    return hero


def _patch_stat_metadata(
    stats: List[Dict[str, Any]], hero: Dict[str, Any], include_hero_info: bool = True
) -> None:
    for entry in stats:
        entry.setdefault("hero_id", hero["id"])
        if include_hero_info:
            entry.setdefault("hero_slug", hero.get("hero_id_slug"))
            entry.setdefault("hero_name", hero.get("name"))


@router.get(
    "/{hero_slug}/skills",
    response_model=List[HeroSkillResponse],
    summary="List skills for a specific hero",
)
async def get_hero_skills(
    hero_slug: str, supabase: Client = Depends(get_supabase_client)
) -> List[Dict[str, Any]]:
    hero = await _hero_or_404(hero_slug, supabase)
    repository = SkillsRepository(supabase)
    skills = await run_in_threadpool(repository.list_by_hero, hero["id"])
    return skills


@router.get(
    "/{hero_slug}/exclusive-gear",
    response_model=List[HeroExclusiveGearResponse],
    summary="List exclusive gear for a specific hero",
)
async def get_hero_exclusive_gear(
    hero_slug: str, supabase: Client = Depends(get_supabase_client)
) -> List[Dict[str, Any]]:
    hero = await _hero_or_404(hero_slug, supabase)
    repository = ExclusiveGearRepository(supabase)
    gear = await run_in_threadpool(repository.list_by_hero_id, hero["id"])
    return gear


@router.get(
    "/{hero_slug}/talents",
    response_model=List[HeroTalentResponse],
    summary="List hero talents",
)
async def get_hero_talents(
    hero_slug: str, supabase: Client = Depends(get_supabase_client)
) -> List[Dict[str, Any]]:
    hero = await _hero_or_404(hero_slug, supabase)
    repository = TalentRepository(supabase)
    talents = await run_in_threadpool(repository.list_by_hero, hero["id"])
    return talents


@router.get(
    "/{hero_slug}/stats",
    response_model=HeroStatsBundleResponse,
    summary="Get both conquest and expedition stats for a hero",
)
async def get_hero_stats(
    hero_slug: str, supabase: Client = Depends(get_supabase_client)
) -> HeroStatsBundleResponse:
    hero = await _hero_or_404(hero_slug, supabase)
    repository = StatsRepository(supabase)
    conquest = await run_in_threadpool(repository.list_conquest_by_hero, hero["id"])
    expedition = await run_in_threadpool(repository.list_expedition_by_hero, hero["id"])
    _patch_stat_metadata(conquest, hero, include_hero_info=False)
    _patch_stat_metadata(expedition, hero, include_hero_info=False)
    return HeroStatsBundleResponse(
        hero_id=hero["id"],
        hero_slug=hero["hero_id_slug"],
        hero_name=hero.get("name"),
        conquest=conquest,
        expedition=expedition,
    )


@router.get(
    "/{hero_slug}/stats/conquest",
    response_model=List[HeroStatsResponse],
    summary="Get conquest stats for a hero",
)
async def get_hero_conquest_stats(
    hero_slug: str, supabase: Client = Depends(get_supabase_client)
) -> List[Dict[str, Any]]:
    hero = await _hero_or_404(hero_slug, supabase)
    repository = StatsRepository(supabase)
    stats = await run_in_threadpool(repository.list_conquest_by_hero, hero["id"])
    _patch_stat_metadata(stats, hero, include_hero_info=False)
    return stats


@router.get(
    "/{hero_slug}/stats/expedition",
    response_model=List[HeroExpeditionStatsResponse],
    summary="Get expedition stats for a hero",
)
async def get_hero_expedition_stats(
    hero_slug: str, supabase: Client = Depends(get_supabase_client)
) -> List[Dict[str, Any]]:
    hero = await _hero_or_404(hero_slug, supabase)
    repository = StatsRepository(supabase)
    stats = await run_in_threadpool(repository.list_expedition_by_hero, hero["id"])
    _patch_stat_metadata(stats, hero, include_hero_info=False)
    return stats
