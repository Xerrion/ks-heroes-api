from fastapi import FastAPI

from db.supabase_client import get_supabase_client

from .routes.heroes import get_all as get_all_heroes
from .routes.heroes import get_all_exclusive_gear
from .routes.heroes import get_by_slug as hero_by_slug
from .routes.heroes import get_exclusive_gear_progression
from .routes.skills import get_all as get_all_skills
from .routes.stats import get_all_conquest, get_all_expedition
from .routes.troops import get_all as get_all_troops
from .routes.vip import get_all as get_all_vip
from .routes.vip import get_by_level as vip_by_level

db = get_supabase_client()
app = FastAPI(
    title="Kingshot Heroes API",
    description="An API for Kingshot hero data.",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "Welcome to the KS-Heroes API"}


app.include_router(get_all_heroes.router, prefix="/heroes", tags=["heroes"])
app.include_router(
    get_all_exclusive_gear.router, prefix="/heroes", tags=["exclusive_gear"]
)
app.include_router(hero_by_slug.router, prefix="/heroes", tags=["heroes detail"])
app.include_router(
    get_exclusive_gear_progression.router, prefix="/heroes", tags=["exclusive_gear"]
)
app.include_router(get_all_skills.router, prefix="/skills", tags=["skills"])
app.include_router(get_all_conquest.router, prefix="/stats", tags=["stats"])
app.include_router(get_all_expedition.router, prefix="/stats", tags=["stats"])
app.include_router(get_all_vip.router, prefix="/vip", tags=["VIP"])
app.include_router(vip_by_level.router, prefix="/vip", tags=["VIP"])
app.include_router(get_all_troops.router, prefix="/troops", tags=["Troops"])
