from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from src.db.repositories.stats import StatsRepository
from src.dependencies import get_supabase_client
from src.schemas.hero import HeroStatsResponse
from supabase import Client

router = APIRouter()


@router.get("/conquest", response_model=List[HeroStatsResponse])
async def get_all_conquest_stats(
    supabase: Client = Depends(get_supabase_client),
):
    """
    Retrieve all hero conquest stats.
    """
    repository = StatsRepository(supabase)
    stats = await run_in_threadpool(repository.list_all_conquest)
    if not stats:
        raise HTTPException(status_code=404, detail="No conquest stats found")
    return stats
