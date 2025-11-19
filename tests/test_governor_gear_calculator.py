import asyncio
from unittest.mock import AsyncMock

import pytest

from src.routes.governor_gear import calculate_gear_stats
from src.schemas.enums import GearRarity, HeroClass
from src.schemas.governor_gear import (
    GearConfiguration,
    GovernorGear,
    GovernorGearCharmLevel,
    GovernorGearCharmSlot,
    GovernorGearLevel,
)


def test_calculate_gear_stats():
    asyncio.run(run_async_test())


async def run_async_test():
    # Mock Repository
    repo = AsyncMock()

    # Mock Data
    levels = [
        GovernorGearLevel(
            level=8,
            rarity=GearRarity.EPIC,
            tier=0,
            stars=1,
            bonuses={"attack_pct": 36.89, "defense_pct": 36.89},
        ),
        GovernorGearLevel(
            level=9,
            rarity=GearRarity.EPIC,
            tier=0,
            stars=2,
            bonuses={"attack_pct": 39.78, "defense_pct": 39.78},
        ),
        GovernorGearLevel(
            level=10,
            rarity=GearRarity.EPIC,
            tier=0,
            stars=3,
            bonuses={"attack_pct": 42.67, "defense_pct": 42.67},
        ),
        GovernorGearLevel(
            level=11,
            rarity=GearRarity.EPIC,
            tier=1,
            stars=0,
            bonuses={"attack_pct": 45.56, "defense_pct": 45.56},
        ),
    ]
    repo.get_all_levels.return_value = levels

    # Mock Gear Data
    all_gear = []
    gear_troop_types = {
        "head": HeroClass.CAVALRY,
        "amulet": HeroClass.CAVALRY,
        "chest": HeroClass.INFANTRY,
        "legs": HeroClass.INFANTRY,
        "ring": HeroClass.ARCHER,
        "staff": HeroClass.ARCHER,
    }
    for gear_id, troop_type in gear_troop_types.items():
        all_gear.append(
            GovernorGear(
                gear_id=gear_id,
                slot=gear_id.capitalize(),
                troop_type=troop_type,
                max_charms=3,
                default_bonus_keys=["attack_pct", "defense_pct"],
            )
        )
    repo.get_all_gear.return_value = all_gear

    charm_levels = [
        GovernorGearCharmLevel(
            level=1, bonuses={"troop_lethality_pct": 9.0, "troop_health_pct": 9.0}
        ),
        GovernorGearCharmLevel(
            level=2, bonuses={"troop_lethality_pct": 12.0, "troop_health_pct": 12.0}
        ),
        GovernorGearCharmLevel(
            level=3, bonuses={"troop_lethality_pct": 16.0, "troop_health_pct": 16.0}
        ),
    ]
    repo.get_all_charm_levels.return_value = charm_levels

    charm_slots = []
    # Define troop types per gear piece to match real game logic
    gear_troop_types = {
        "head": HeroClass.CAVALRY,
        "amulet": HeroClass.CAVALRY,
        "chest": HeroClass.INFANTRY,
        "legs": HeroClass.INFANTRY,
        "ring": HeroClass.ARCHER,
        "staff": HeroClass.ARCHER,
    }

    for gear_id in ["head", "amulet", "chest", "legs", "ring", "staff"]:
        for i in range(1, 4):
            charm_slots.append(
                GovernorGearCharmSlot(
                    id=1,
                    gear_id=gear_id,
                    slot_index=i,
                    troop_type=gear_troop_types[gear_id],
                    bonus_keys=["troop_lethality_pct", "troop_health_pct"],
                )
            )
    repo.get_all_charm_slots.return_value = charm_slots

    # User Configuration
    config = [
        GearConfiguration(
            gear_id="head",
            rarity=GearRarity.EPIC,
            tier=0,
            stars=1,
            gem_levels=[1, 1, 1],
        ),
        GearConfiguration(
            gear_id="amulet",
            rarity=GearRarity.EPIC,
            tier=0,
            stars=1,
            gem_levels=[1, 1, 1],
        ),
        GearConfiguration(
            gear_id="chest",
            rarity=GearRarity.EPIC,
            tier=1,
            stars=0,
            gem_levels=[2, 2, 2],
        ),
        GearConfiguration(
            gear_id="legs",
            rarity=GearRarity.EPIC,
            tier=0,
            stars=3,
            gem_levels=[2, 2, 2],
        ),
        GearConfiguration(
            gear_id="ring",
            rarity=GearRarity.EPIC,
            tier=0,
            stars=2,
            gem_levels=[2, 2, 2],
        ),
        GearConfiguration(
            gear_id="staff",
            rarity=GearRarity.EPIC,
            tier=0,
            stars=2,
            gem_levels=[3, 2, 1],
        ),
    ]

    result = await calculate_gear_stats(config, repo)

    print("\nTotal Bonuses:")
    for k, v in result.total_bonuses.items():
        print(f"{k}: {v}")

    # Basic assertions
    # Head: 36.89 * 2 (Head+Amulet) + 45.56 (Chest) + 42.67 (Legs) + 39.78 * 2 (Ring+Staff)
    # 36.89*2 + 45.56 + 42.67 + 39.78*2 = 73.78 + 45.56 + 42.67 + 79.56 = 241.57
    # expected_attack = 36.89 * 2 + 45.56 + 42.67 + 39.78 * 2
    # assert abs(result.total_bonuses["attack_pct"] - expected_attack) < 0.01

    # Now attack/defense are split by troop type
    # Cavalry (Head + Amulet): 36.89 * 2 = 73.78
    assert (
        abs(result.total_bonuses.get("cavalry", {}).get("attack_pct", 0) - 73.78) < 0.01
    )
    assert (
        abs(result.total_bonuses.get("cavalry", {}).get("defense_pct", 0) - 73.78)
        < 0.01
    )

    # Infantry (Chest + Legs): 45.56 + 42.67 = 88.23
    assert (
        abs(result.total_bonuses.get("infantry", {}).get("attack_pct", 0) - 88.23)
        < 0.01
    )
    assert (
        abs(result.total_bonuses.get("infantry", {}).get("defense_pct", 0) - 88.23)
        < 0.01
    )

    # Archer (Ring + Staff): 39.78 * 2 = 79.56
    assert (
        abs(result.total_bonuses.get("archer", {}).get("attack_pct", 0) - 79.56) < 0.01
    )
    assert (
        abs(result.total_bonuses.get("archer", {}).get("defense_pct", 0) - 79.56) < 0.01
    )

    # Gems:
    # Lvl 1: 9.0
    # Lvl 2: 12.0
    # Lvl 3: 16.0

    # Cavalry (Head + Amulet):
    # Head: 3x Lvl 1 = 27.0
    # Amulet: 3x Lvl 1 = 27.0
    # Total Cavalry Lethality = 54.0
    assert (
        abs(result.total_bonuses.get("cavalry", {}).get("lethality_pct", 0) - 54.0)
        < 0.01
    )

    # Infantry (Chest + Legs):
    # Chest: 3x Lvl 2 = 36.0
    # Legs: 3x Lvl 2 = 36.0
    # Total Infantry Lethality = 72.0
    assert (
        abs(result.total_bonuses.get("infantry", {}).get("lethality_pct", 0) - 72.0)
        < 0.01
    )

    # Archer (Ring + Staff):
    # Ring: 3x Lvl 2 = 36.0
    # Staff: 1x Lvl 3 (16) + 1x Lvl 2 (12) + 1x Lvl 1 (9) = 37.0
    # Total Archer Lethality = 73.0
    assert (
        abs(result.total_bonuses.get("archer", {}).get("lethality_pct", 0) - 73.0)
        < 0.01
    )
