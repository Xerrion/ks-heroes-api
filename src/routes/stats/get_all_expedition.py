from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from src.db.repositories.stats import StatsRepository
from src.dependencies import get_supabase_client
from src.schemas.hero import HeroExpeditionStatsResponse
from supabase import Client

router = APIRouter()


@router.get("/expedition", response_model=List[HeroExpeditionStatsResponse])
async def get_all_expedition_stats(
    supabase: Client = Depends(get_supabase_client),
):
    """
    Retrieve all hero expedition stats.
    """
    repository = StatsRepository(supabase)
    stats = await run_in_threadpool(repository.list_all_expedition)
    if not stats:
        raise HTTPException(status_code=404, detail="No expedition stats found")
    return stats
