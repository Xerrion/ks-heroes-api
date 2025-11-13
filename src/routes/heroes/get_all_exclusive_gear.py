from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from src.db.repositories.exclusive_gear import ExclusiveGearRepository
from src.dependencies import get_supabase_client
from src.schemas.exclusive_gear import HeroExclusiveGearResponse
from supabase import Client

router = APIRouter()


@router.get("/exclusive-gear", response_model=List[HeroExclusiveGearResponse])
async def get_all_exclusive_gear(
    supabase: Client = Depends(get_supabase_client),
):
    """
    Retrieve all hero exclusive gear.
    """
    repository = ExclusiveGearRepository(supabase)
    try:
        data = await run_in_threadpool(repository.list_all)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not data:
        raise HTTPException(status_code=404, detail="No exclusive gear found")
    return data
