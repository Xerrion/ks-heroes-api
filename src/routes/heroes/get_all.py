from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from src.db.repositories.hero import HeroRepository
from src.dependencies import get_supabase_client
from src.schemas.hero import HeroBasicResponse
from supabase import Client

router = APIRouter()


@router.get("/", response_model=List[HeroBasicResponse])
async def get_all_heroes(
    supabase: Client = Depends(get_supabase_client),
):
    """
    Retrieve all heroes with basic information.
    """
    repository = HeroRepository(supabase)
    heroes = await run_in_threadpool(repository.list_all)
    if not heroes:
        raise HTTPException(status_code=404, detail="No heroes found")
    return heroes
