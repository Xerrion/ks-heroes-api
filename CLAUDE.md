# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kingshot Hero API is a **data layer** for Kingshot hero data built on Supabase (PostgreSQL). It provides structured, queryable hero stats, skills, expedition bonuses, and exclusive gear. **This project does NOT include battle simulation or damage formulas**  it only serves normalized data for external simulators and tools.

## Development Commands

### Database Operations

- **Reset and migrate database**: `supabase db reset` (resets local DB and applies all migrations)
- **Apply migrations**: `supabase db push` (pushes local migrations to remote)
- **Generate seed SQL**: `python scripts/generate_seed_sql.py --heroes data/heroes.json --skills data/hero_skills.json --gear data/exclusive_gear.json --output seed.sql`

### Asset Management

- **Upload assets to Supabase Storage**: `python scripts/upload_assets.py` (uploads images from `assets/` directory)
- **Organize local assets**: `python scripts/organize_assets.py` (reorganizes image files)

### Running Tests

- **Run tests**: `pytest` (test directory path is configured in pyproject.toml)

### Dependencies

- **Install dependencies**: `uv pip install -e .`

## Environment Configuration

Create a `.env` file with these required variables:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY` or `SUPABASE_SERVICE_ROLE_KEY`: Auth key for Supabase
- `SUPABASE_STORAGE_BUCKET`: Storage bucket name (defaults to `assets`)

Reference `.env.example` for the exact format.

## Architecture

### Database Schema

The Supabase PostgreSQL database has these tables:

- `heroes`: Core hero identity (slug, name, class, rarity, generation)
- `hero_conquest_stats`: Base hero attack/defense/health
- `hero_expedition_stats`: Expedition troop bonuses (%, troop_type-specific)
- `hero_skills`: Skills with classification (Base/Conquest/Expedition)
- `hero_skill_levels`: Level-based skill scaling (Lv1-5)
- `hero_exclusive_gear`: Exclusive gear per hero
- `hero_exclusive_gear_levels`: Gear stats for levels 1-10
- `hero_exclusive_gear_skills`: Gear-specific Conquest/Expedition skill upgrades

### RPC Endpoints

- `api_get_hero(slug)`: Returns complete hero data as JSON (stats, skills, expedition bonuses, exclusive gear)

### Python Modules

- `src/settings.py`: Loads Supabase config from environment using Pydantic
- `src/supabase_client.py`: Factory for the shared Supabase client (memoized)
- `src/storage.py`: Supabase Storage helpers (upload files/directories, build public URLs)
- `scripts/generate_seed_sql.py`: Generates SQL INSERT statements from JSON data files
- `scripts/upload_assets.py`: Uploads hero/skill/gear images to Supabase Storage
- `scripts/organize_assets.py`: Reorganizes local asset files

### Data Files

- `data/heroes.json`: Array of heroes with id, name, generation, rarity, class
- `data/hero_skills.json`: Skills with levels and effects per hero
- `data/exclusive_gear.json`: Exclusive gear with level-based stats
- Nested data directories: `data/conquest/`, `data/expedition/`, `data/exclusive/`

### Migrations

All database schema is defined in `supabase/migrations/`. Migrations are applied in order by filename timestamp. Key migration files:

- `20251106120414_init_types_and_functions.sql`: Base types and helper functions
- `20251106120442_create_heroes.sql`: Heroes table
- `202511061737*.sql`: Stats, skills, and skill levels tables
- `202511061739*.sql`: Exclusive gear tables
- `20251106174101_create_rpc_api_get_hero.sql`: RPC function for JSON API

## Code Conventions

- **Python version**: 3.13+
- **Dependency management**: Use `uv` for package installation
- **Settings**: All config comes from environment via Pydantic models (see `src/settings.py`)
- **Supabase client**: Always use `get_supabase_client()` from `src/supabase_client.py`  it is memoized and shared
- **SQL generation**: The `generate_seed_sql.py` script uses subselects to resolve foreign keys, avoiding hardcoded UUIDs
- **Asset paths**: Store relative paths in database; build public URLs with `build_public_asset_url()` from `src/storage.py`
- **Normalization**: Enums for class (Infantry/Cavalry/Archer), rarity (Rare/Epic/Mythic), skill_type (Active/Passive/Talent), battle_type (Base/Conquest/Expedition) are enforced in SQL and Python
