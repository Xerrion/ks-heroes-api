"""Enums for type-safe API parameters and responses.

This module contains all enum definitions used across the API for:
- Hero attributes (generation, rarity, class)
- Skill attributes (type, level, mode)
- Troop attributes (type, level)
- Stat types
"""

from enum import Enum


class HeroGeneration(int, Enum):
    """Hero generation (1, 2, or 3)."""

    GENERATION_1 = 1
    GENERATION_2 = 2
    GENERATION_3 = 3


class HeroRarity(str, Enum):
    """Hero rarity levels.

    Maps to in-game display:
    - Rare = R
    - Epic = SR
    - Mythic = SSR
    """

    RARE = "Rare"
    EPIC = "Epic"
    MYTHIC = "Mythic"


class HeroClass(str, Enum):
    """Hero class types."""

    INFANTRY = "Infantry"
    CAVALRY = "Cavalry"
    ARCHER = "Archer"


class SkillType(str, Enum):
    """Skill types."""

    ACTIVE = "Active"
    PASSIVE = "Passive"


class SkillLevel(int, Enum):
    """Skill levels (1-5)."""

    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5


class GameMode(str, Enum):
    """Game modes."""

    CONQUEST = "conquest"
    EXPEDITION = "expedition"


class TroopType(str, Enum):
    """Troop types."""

    INFANTRY = "infantry"
    CAVALRY = "cavalry"
    ARCHER = "archer"


class TroopLevel(int, Enum):
    """Troop levels (1-11)."""

    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7
    LEVEL_8 = 8
    LEVEL_9 = 9
    LEVEL_10 = 10
    LEVEL_11 = 11


class TroopTGLevel(int, Enum):
    """Troop Training Ground levels (1-11)."""

    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7
    LEVEL_8 = 8
    LEVEL_9 = 9
    LEVEL_10 = 10
    LEVEL_11 = 11


class StatType(str, Enum):
    """Stat types for heroes."""

    ATTACK = "attack"
    DEFENSE = "defense"
    HEALTH = "health"
