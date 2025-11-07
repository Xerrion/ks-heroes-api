from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from supabase import Client

from ...dependencies import get_supabase_client
from ...schemas.exclusive_gear import HeroExclusiveGearResponse

router = APIRouter()


@router.get("/exclusive-gear", response_model=List[HeroExclusiveGearResponse])
async def get_all_exclusive_gear(
    supabase: Client = Depends(get_supabase_client),
):
    """
    Retrieve all hero exclusive gear.
    """
    query = supabase.table("hero_exclusive_gear").select(
        "*, levels:hero_exclusive_gear_levels(*), skills:hero_exclusive_gear_skills(*)"
    )
    response = await run_in_threadpool(query.execute)
    if not response.data:
        raise HTTPException(status_code=404, detail="No exclusive gear found")
    return response.data
