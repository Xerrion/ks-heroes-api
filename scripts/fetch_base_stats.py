#!/usr/bin/env python3
"""Fetch hero base & expedition stats from kingshotdata.com and update local data files."""

from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class HeroSource:
    slug: str
    hero_id: str


@dataclass
class ExpeditionStats:
    troop_type: str
    attack_pct: float | None = None
    defense_pct: float | None = None


@dataclass
class HeroStats:
    attack: int
    defense: int
    health: int
    expedition: ExpeditionStats | None
    source_url: str


HERO_SOURCES: tuple[HeroSource, ...] = (
    HeroSource("rosa", "rosa"),
    HeroSource("alcar", "alcar"),
    HeroSource("margot", "margot"),
    HeroSource("jaeger", "jaeger"),
    HeroSource("eric", "eric"),
    HeroSource("petra", "petra"),
    HeroSource("hilde", "hilde"),
    HeroSource("zoe", "zoe"),
    HeroSource("marlin", "marlin"),
    HeroSource("jabel", "jabel"),
    HeroSource("amadeus", "amadeus"),
    HeroSource("helga", "helga"),
    HeroSource("saul", "saul"),
    HeroSource("mikoto", "amane"),
    HeroSource("yeonwoo", "yeonwoo"),
    HeroSource("chenko", "chenko"),
    HeroSource("fahd", "fahd"),
    HeroSource("gordon", "gordon"),
    HeroSource("diana", "diana"),
    HeroSource("howard", "howard"),
    HeroSource("quinn", "quinn"),
    HeroSource("olive", "olive"),
    HeroSource("edwin", "edwin"),
    HeroSource("seth", "seth"),
    HeroSource("forrest", "forrest"),
)

STAT_PATTERNS = {
    "attack": re.compile(r"Hero Attack:</strong>\s*([\d,]+)", re.IGNORECASE),
    "defense": re.compile(r"Hero Defense:</strong>\s*([\d,]+)", re.IGNORECASE),
    "health": re.compile(r"Hero Health:</strong>\s*([\d,]+)", re.IGNORECASE),
}

EXPEDITION_PATTERN = re.compile(
    r"<strong>(Archer|Infantry|Cavalry)\s+(Attack|Defense):</strong>\s*\+?([\d.,]+)%",
    re.IGNORECASE,
)

DEFAULT_BASE_URL = "https://kingshotdata.com/heroes/{slug}/"


def fetch_html(url: str, timeout: int, verify: bool) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    context = ssl.create_default_context() if verify else ssl._create_unverified_context()  # type: ignore[attr-defined]
    with urlopen(request, timeout=timeout, context=context) as response:  # nosec B310
        return response.read().decode("utf-8", errors="ignore")


def parse_stat_value(match: str) -> int:
    return int(match.replace(",", ""))


def _parse_percent(value: str) -> float:
    return float(value.replace(",", ""))


def extract_expedition_stats(html: str) -> ExpeditionStats | None:
    heading_match = re.search(r"<h2[^>]*id=\"expedition\"[^>]*>", html, re.IGNORECASE)
    if not heading_match:
        return None
    start = heading_match.end()
    remainder = html[start:]
    next_heading = re.search(r"<h2[^>]*id=\"", remainder, re.IGNORECASE)
    end = next_heading.start() if next_heading else len(remainder)
    section = remainder[:end]
    matches = EXPEDITION_PATTERN.findall(section)
    if not matches:
        return None
    primary_troop = matches[0][0].capitalize()
    stats: dict[str, float | None] = {"attack": None, "defense": None}
    for troop, stat_type, value in matches:
        if troop.lower() != primary_troop.lower():
            continue
        key = stat_type.lower()
        stats[key] = _parse_percent(value)
    if all(v is None for v in stats.values()):
        return None
    return ExpeditionStats(
        troop_type=primary_troop,
        attack_pct=stats["attack"],
        defense_pct=stats["defense"],
    )


def extract_stats(html: str, url: str) -> HeroStats:
    values = {}
    for key, pattern in STAT_PATTERNS.items():
        matches = pattern.findall(html)
        if not matches:
            raise ValueError(f"Missing {key} value in {url}")
        values[key] = parse_stat_value(matches[0])
    expedition = extract_expedition_stats(html)
    return HeroStats(
        attack=values["attack"],
        defense=values["defense"],
        health=values["health"],
        expedition=expedition,
        source_url=url,
    )


def fetch_stats_for_heroes(
    heroes: Iterable[HeroSource],
    *,
    base_url: str,
    timeout: int,
    verify: bool,
) -> OrderedDict[str, HeroStats]:
    results: OrderedDict[str, HeroStats] = OrderedDict()
    errors: list[tuple[HeroSource, Exception]] = []
    for hero in heroes:
        url = base_url.format(slug=hero.slug)
        try:
            html = fetch_html(url, timeout, verify)
            stats = extract_stats(html, url)
        except (HTTPError, URLError, ValueError) as exc:
            errors.append((hero, exc))
            continue
        results[hero.hero_id] = stats
        expedition_note = ""
        if stats.expedition:
            exp = stats.expedition
            parts: list[str] = []
            if exp.attack_pct is not None:
                parts.append(f"atk {exp.attack_pct:g}%")
            if exp.defense_pct is not None:
                parts.append(f"def {exp.defense_pct:g}%")
            if parts:
                expedition_note = f" | expedition {exp.troop_type}: " + ", ".join(parts)
        print(
            f"Fetched {hero.hero_id:7s} -> attack {stats.attack}, defense {stats.defense}, health {stats.health}{expedition_note}"
        )
    if errors:
        for hero, exc in errors:
            print(
                f"Error fetching {hero.hero_id} ({hero.slug}): {exc}", file=sys.stderr
            )
        raise RuntimeError("Failed to fetch stats for all heroes")
    return results


def update_heroes_json(path: Path, stats_map: OrderedDict[str, HeroStats]) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    index = {entry.get("id"): entry for entry in data if isinstance(entry, dict)}
    missing = sorted(set(stats_map.keys()) - set(index.keys()))
    if missing:
        raise RuntimeError(f"Heroes missing from {path}: {', '.join(missing)}")

    updated = 0
    for hero_id, stats in stats_map.items():
        entry = index[hero_id]
        entry["base_stats"] = {
            "attack": stats.attack,
            "defense": stats.defense,
            "health": stats.health,
        }
        entry["base_attack"] = stats.attack
        entry["base_defense"] = stats.defense
        entry["base_health"] = stats.health
        if stats.expedition:
            exp = stats.expedition
            entry["expedition_stats"] = {
                "troop_type": exp.troop_type,
                "attack_pct": exp.attack_pct,
                "defense_pct": exp.defense_pct,
            }
        updated += 1
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return updated


def write_migration(
    directory: Path,
    stats_map: OrderedDict[str, HeroStats],
    *,
    timestamp: str | None,
    migration_name: str,
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{migration_name}.sql"
    path = directory / filename
    if path.exists():
        raise FileExistsError(f"Migration already exists: {path}")

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = [
        f"-- Auto-generated by fetch_base_stats.py on {generated}",
        "",
    ]

    def fmt(value: float | int | None) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, float):
            return (f"{value:.6f}").rstrip("0").rstrip(".")
        return str(value)

    for hero_id, stats in stats_map.items():
        lines.extend(
            [
                "INSERT INTO hero_conquest_stats (hero_id, attack, defense, health)",
                f"SELECT h.id, {stats.attack}, {stats.defense}, {stats.health}",
                f"FROM heroes h WHERE h.hero_id_slug = '{hero_id}'",
                "ON CONFLICT (hero_id) DO UPDATE",
                "SET attack = EXCLUDED.attack,",
                "    defense = EXCLUDED.defense,",
                "    health = EXCLUDED.health;",
                "",
            ]
        )
        if stats.expedition:
            exp = stats.expedition
            if exp.attack_pct is None and exp.defense_pct is None:
                continue
            lines.extend(
                [
                    "INSERT INTO hero_expedition_stats (hero_id, troop_type, attack_pct, defense_pct)",
                    f"SELECT h.id, '{exp.troop_type}', {fmt(exp.attack_pct)}, {fmt(exp.defense_pct)}",
                    f"FROM heroes h WHERE h.hero_id_slug = '{hero_id}'",
                    "ON CONFLICT (hero_id) DO UPDATE",
                    "SET troop_type = EXCLUDED.troop_type,",
                    "    attack_pct = EXCLUDED.attack_pct,",
                    "    defense_pct = EXCLUDED.defense_pct;",
                    "",
                ]
            )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Kingshot hero base stats and update local data",
    )
    parser.add_argument(
        "--heroes-json",
        type=Path,
        default=Path("data/heroes.json"),
        help="Path to heroes.json (default: data/heroes.json)",
    )
    parser.add_argument(
        "--migrations-dir",
        type=Path,
        default=Path("supabase/migrations"),
        help="Directory where the migration should be written (default: supabase/migrations)",
    )
    parser.add_argument(
        "--migration-name",
        default="populate_hero_base_stats",
        help="Suffix for the migration filename (default: populate_hero_base_stats)",
    )
    parser.add_argument(
        "--timestamp",
        help="Optional timestamp prefix for the migration (format: YYYYMMDDHHMMSS)",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL template with {slug} placeholder (default: Kingshot heroes)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Network timeout in seconds (default: 20)",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification (use with caution)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stats_map = fetch_stats_for_heroes(
        HERO_SOURCES,
        base_url=args.base_url,
        timeout=args.timeout,
        verify=not args.insecure,
    )
    updated = update_heroes_json(args.heroes_json, stats_map)
    migration_path = write_migration(
        args.migrations_dir,
        stats_map,
        timestamp=args.timestamp,
        migration_name=args.migration_name,
    )
    print(f"Updated {updated} heroes in {args.heroes_json}")
    print(f"Wrote migration to {migration_path}")


if __name__ == "__main__":
    main()
