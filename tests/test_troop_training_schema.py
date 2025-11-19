"""Tests for troop training data schema and validation."""

import pytest
from pydantic import ValidationError

from src.schemas.troops import Troop, TroopsGroupedByType, TroopStats, TroopType


def test_troop_with_training_data():
    """Test that Troop model accepts training data."""
    troop_data = {
        "id": 1,
        "troop_type": "Infantry",
        "troop_level": 5,
        "true_gold_level": 0,
        "attack": 7,
        "defense": 10,
        "health": 12,
        "lethality": 6,
        "power": 15,
        "load": 188,
        "speed": 11,
        "bread": 156,
        "wood": 117,
        "stone": 27,
        "iron": 6,
        "training_time_seconds": 44,
        "training_power": 13,
        "hog_event_points": 385,
        "kvk_event_points": 12,
        "sg_event_points": 7,
    }

    troop = Troop.model_validate(troop_data)

    assert troop.bread == 156
    assert troop.wood == 117
    assert troop.stone == 27
    assert troop.iron == 6
    assert troop.training_time_seconds == 44
    assert troop.training_power == 13
    assert troop.hog_event_points == 385
    assert troop.kvk_event_points == 12
    assert troop.sg_event_points == 7


def test_troop_without_training_data():
    """Test that Troop model works without training data (legacy compatibility)."""
    troop_data = {
        "id": 1,
        "troop_type": "Infantry",
        "troop_level": 5,
        "true_gold_level": 0,
        "attack": 7,
        "defense": 10,
        "health": 12,
        "lethality": 6,
        "power": 15,
        "load": 188,
        "speed": 11,
    }

    troop = Troop.model_validate(troop_data)

    # Training fields should be None
    assert troop.bread is None
    assert troop.wood is None
    assert troop.training_time_seconds is None
    assert troop.hog_event_points is None


def test_troop_stats_with_training_and_events():
    """Test TroopStats with training and events data."""
    stats_data = {
        "troop_level": 10,
        "true_gold_level": 0,
        "stats": {
            "attack": 20,
            "defense": 26,
            "health": 30,
            "lethality": 20,
            "power": 132,
            "load": 758,
            "speed": 14,
        },
        "training": {
            "bread": 2440,
            "wood": 2301,
            "stone": 474,
            "iron": 109,
            "training_time_seconds": 152,
            "training_power": 66,
        },
        "events": {
            "hog_event_points": 1960,
            "kvk_event_points": 60,
            "sg_event_points": 39,
        },
    }

    troop_stats = TroopStats.model_validate(stats_data)

    assert troop_stats.training is not None
    assert troop_stats.training["bread"] == 2440
    assert troop_stats.training["training_time_seconds"] == 152

    assert troop_stats.events is not None
    assert troop_stats.events["hog_event_points"] == 1960
    assert troop_stats.events["kvk_event_points"] == 60


def test_troop_stats_without_training():
    """Test TroopStats without training data."""
    stats_data = {
        "troop_level": 5,
        "true_gold_level": 0,
        "stats": {
            "attack": 7,
            "defense": 10,
            "health": 12,
            "lethality": 6,
            "power": 15,
            "load": 188,
            "speed": 11,
        },
    }

    troop_stats = TroopStats.model_validate(stats_data)

    assert troop_stats.training is None
    assert troop_stats.events is None


def test_grouped_troops_with_training():
    """Test TroopsGroupedByType with training data."""
    grouped_data = {
        "Infantry": [
            {
                "troop_level": 5,
                "true_gold_level": 0,
                "stats": {
                    "attack": 7,
                    "defense": 10,
                    "health": 12,
                    "lethality": 6,
                    "power": 15,
                    "load": 188,
                    "speed": 11,
                },
                "training": {
                    "bread": 156,
                    "wood": 117,
                    "stone": 27,
                    "iron": 6,
                    "training_time_seconds": 44,
                    "training_power": 13,
                },
                "events": {
                    "hog_event_points": 385,
                    "kvk_event_points": 12,
                    "sg_event_points": 7,
                },
            }
        ],
        "Cavalry": [],
        "Archer": [],
    }

    grouped = TroopsGroupedByType.model_validate(grouped_data)

    assert len(grouped.Infantry) == 1
    assert grouped.Infantry[0].training is not None
    assert grouped.Infantry[0].training["bread"] == 156
    assert grouped.Infantry[0].events is not None
    assert grouped.Infantry[0].events["hog_event_points"] == 385


def test_troop_validation_negative_resources():
    """Test that negative resource values are rejected."""
    troop_data = {
        "id": 1,
        "troop_type": "Infantry",
        "troop_level": 5,
        "true_gold_level": 0,
        "attack": 7,
        "defense": 10,
        "health": 12,
        "lethality": 6,
        "power": 15,
        "load": 188,
        "speed": 11,
        "bread": -100,  # Invalid negative value
    }

    with pytest.raises(ValidationError) as exc_info:
        Troop.model_validate(troop_data)

    assert "bread" in str(exc_info.value)


def test_all_troop_types_training_data():
    """Test that all troop types can have training data."""
    for troop_type in ["Infantry", "Cavalry", "Archer"]:
        troop_data = {
            "id": 1,
            "troop_type": troop_type,
            "troop_level": 10,
            "true_gold_level": 0,
            "attack": 20,
            "defense": 26,
            "health": 30,
            "lethality": 20,
            "power": 132,
            "load": 758,
            "speed": 14,
            "bread": 2440,
            "wood": 2301,
            "stone": 474,
            "iron": 109,
            "training_time_seconds": 152,
            "training_power": 66,
            "hog_event_points": 1960,
            "kvk_event_points": 60,
            "sg_event_points": 39,
        }

        troop = Troop.model_validate(troop_data)
        assert troop.troop_type.value == troop_type
        assert troop.bread == 2440
