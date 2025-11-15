from fastapi import FastAPI

from src.db.supabase_client import get_supabase_client
from src.routes import (
    exclusive_gear,
    governor_gear,
    heroes,
    skills,
    stats,
    talents,
    troops,
    vip,
)

db = get_supabase_client()
app = FastAPI(
    title="Kingshot Heroes API",
    description="An API for Kingshot hero data.",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "Welcome to the KS-Heroes API"}


# Include routers - each module exports a configured router with prefix and tags
app.include_router(heroes.router)
app.include_router(skills.router)
app.include_router(stats.router)
app.include_router(exclusive_gear.router)
app.include_router(talents.router)
app.include_router(troops.router)
app.include_router(vip.router)
app.include_router(governor_gear.router)
