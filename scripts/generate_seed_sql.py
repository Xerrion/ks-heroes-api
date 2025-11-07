#!/usr/bin/env python3
"""
generate_seed_sql.py

Create a Supabase-ready seed.sql from Kingshot Hero API JSON files, with defaults to ./data/*.json.
Handles expedition skills living in hero_skills.json (partitioned arrays or unified array).
Also supports exclusive gear JSON keyed by hero name or as an array.

Usage:
  python generate_seed_sql.py \
    --heroes ./data/heroes.json \
    --skills ./data/hero_skills.json \
    --gear ./data/exclusive_gear.json \
        --conquest-stats ./data/heroes_conquest_base.json \
        --expedition-stats ./data/heroes_expedition_base.json \
    --output seed.sql
"""

import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable

ALLOWED_CLASSES = {"Infantry", "Cavalry", "Archer"}
ALLOWED_RARITIES = {"Rare", "Epic", "Mythic"}
ALLOWED_SKILL_TYPES = {
    "Active",
    "Passive",
    "Talent",
    "Expedition",
    "Conquest",
}  # tolerant to data


def slugify(text: str) -> str:
    import re

    t = (text or "").strip().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


def sql_str(value):
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def sql_json(value):
    if value is None:
        return "NULL"
    return sql_str(json.dumps(value, ensure_ascii=False))


def coalesce_int(v):
    if v is None:
        return "NULL"
    try:
        return str(int(v))
    except Exception:
        try:
            return str(int(float(v)))
        except Exception:
            return "NULL"


def coalesce_decimal(v):
    if v is None:
        return "NULL"
    try:
        dec = Decimal(str(v))
    except (InvalidOperation, ValueError, TypeError):
        return "NULL"
    normalized = dec.normalize()
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def normalize_class(c):
    if not c:
        return None
    c2 = str(c).strip().capitalize()
    return c2 if c2 in ALLOWED_CLASSES else None


def normalize_rarity(r):
    if not r:
        return None
    r2 = str(r).strip().capitalize()
    return r2 if r2 in ALLOWED_RARITIES else None


def normalize_skill_type(t):
    # Accept both "Active/Passive/Talent" and sloppy "Expedition/Conquest"
    if not t:
        return "Passive"
    t2 = str(t).strip().capitalize()
    return t2 if t2 in ALLOWED_SKILL_TYPES else "Passive"


def default_hero_image_path(slug: str) -> str:
    return f"heroes/{slug}.png"


def default_talent_icon_path(hero_slug: str) -> str:
    return f"talents/{hero_slug}.png"


def default_skill_icon_path(hero_slug: str, skill_name: str) -> str:
    return f"skills/{hero_slug}/{slugify(skill_name)}.png"


def default_exclusive_skill_icon_path(hero_slug: str, skill_name: str) -> str:
    return f"exclusive/skills/{hero_slug}/{slugify(skill_name)}.png"


def default_gear_image_path(gear_name: str) -> str:
    return f"exclusive/gear/{slugify(gear_name)}.png"


def iter_level_items(levels):
    if not levels:
        return []
    if isinstance(levels, dict):
        items = []
        for k, v in levels.items():
            try:
                lvl = int(k)
            except Exception:
                continue
            items.append((lvl, v or {}))
        items.sort(key=lambda x: x[0])
        return items
    if isinstance(levels, list):
        return list(enumerate(levels, start=1))
    return []


def normalize_skill_effect(effect):
    """Normalize skill effect data into a consistent JSON object."""
    if isinstance(effect, str):
        return {"description": effect}
    if isinstance(effect, dict):
        return effect
    return None


def build_effects_payload(skill: dict | None) -> dict:
    if not skill:
        return {}
    levels = [
        {"level": lvl, **(data or {})}
        for lvl, data in iter_level_items(skill.get("levels"))
    ]
    payload: dict[str, object] = {}
    if levels:
        payload["levels"] = levels
    summary = skill.get("effects")
    if summary:
        payload["summary"] = summary
    if not payload and skill.get("description"):
        payload["description"] = skill.get("description")
    return payload


def guess_battle_type(skill_obj, forced=None):
    if forced:
        return forced
    # Try explicit hints
    for key in ("battle_type", "mode", "category"):
        v = skill_obj.get(key)
        if v:
            vv = str(v).strip().capitalize()
            if vv in {"Base", "Conquest", "Expedition"}:
                return vv
            if "conquest" in str(v).lower():
                return "Conquest"
            if "expedition" in str(v).lower():
                return "Expedition"
    # Heuristic from type/name/description
    t = (skill_obj.get("type") or "").strip().lower()
    if t in {"conquest", "expedition", "base"}:
        return t.capitalize()
    name = (skill_obj.get("name") or "").lower()
    desc = (skill_obj.get("description") or "").lower()
    if "conquest" in name or any(k in desc for k in ["arena", "bustling inn"]):
        return "Conquest"
    if any(
        k in desc
        for k in [
            "rally",
            "fort",
            "city",
            "bear trap",
            "viking",
            "sanctuary",
            "defending",
            "attacking",
        ]
    ):
        return "Expedition"
    return "Base"


def iter_heroes(data):
    """Yield normalized hero dicts from heroes.json (list or dict)."""
    if isinstance(data, dict):
        for k, v in data.items():
            obj = dict(v or {})
            obj.setdefault("id", obj.get("id") or slugify(obj.get("name") or k))
            yield obj
    elif isinstance(data, list):
        for v in data:
            v = v or {}
            v.setdefault("id", v.get("id") or slugify(v.get("name") or ""))
            yield v


def collect_skills(obj):
    """
    Returns iterable of (hero_slug, skill_obj, battle_type).
    Supports:
      - Partitioned: { hero_id, conquest_skills:[], expedition_skills:[], talent: {...} }
      - Unified:     { hero_id, skills:[ {battle_type/mode/category}, ... ] }
    """
    if isinstance(obj, dict):
        entries = obj.get("heroes", list(obj.values()))
    elif isinstance(obj, list):
        entries = obj
    else:
        entries = []

    for e in entries:
        hero_slug = e.get("hero_id") or slugify(e.get("hero") or e.get("name") or "")
        if not hero_slug:
            continue
        # Unified array
        for s in e.get("skills") or []:
            yield hero_slug, s, guess_battle_type(s)
        # Partitioned arrays
        for s in e.get("conquest_skills") or []:
            yield hero_slug, s, "Conquest"
        for s in e.get("expedition_skills") or []:
            yield hero_slug, s, "Expedition"
        if e.get("talent"):
            yield hero_slug, e["talent"], "Base"


def build_exclusive_skill_lookup(obj):
    lookup: dict[tuple[str, str], dict] = {}
    entries: Iterable[dict] = []
    if isinstance(obj, dict):
        entries = obj.get("heroes", list(obj.values()))  # type: ignore[assignment]
    elif isinstance(obj, list):
        entries = obj
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        hero_slug = slugify(
            entry.get("hero_id") or entry.get("hero") or entry.get("name") or ""
        )
        if not hero_slug:
            continue
        for skill in entry.get("exclusive_skills", []) or []:
            name = skill.get("name")
            if not name:
                continue
            lookup[(hero_slug, name)] = skill
    return lookup


def iter_gear(data):
    """Yield gear entries normalized with hero_id and levels dict."""
    if data is None:
        return
    if isinstance(data, dict):
        for k, g in data.items():
            entry = dict(g or {})
            entry.setdefault("hero_id", entry.get("hero_id") or slugify(k))
            yield entry
    elif isinstance(data, list):
        for g in data:
            yield g


def iter_entries(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        heroes = data.get("heroes")
        if isinstance(heroes, list):
            return heroes
        return list(data.values())
    return []


def main():
    repo_root = Path.cwd()
    default_data = repo_root / "data"
    ap = argparse.ArgumentParser()
    ap.add_argument("--heroes", default=str(default_data / "heroes.json"))
    ap.add_argument("--skills", default=str(default_data / "hero_skills.json"))
    ap.add_argument("--gear", default=str(default_data / "exclusive_gear.json"))
    ap.add_argument(
        "--conquest-stats",
        default=str(default_data / "heroes_conquest_base.json"),
        help="Path to conquest base stats JSON (default: data/heroes_conquest_base.json)",
    )
    ap.add_argument(
        "--expedition-stats",
        default=str(default_data / "heroes_expedition_base.json"),
        help="Path to expedition base stats JSON (default: data/heroes_expedition_base.json)",
    )
    ap.add_argument("--output", default="seed.sql")
    args = ap.parse_args()

    # Load JSON
    def load_or_none(p):
        pth = Path(p)
        return json.loads(pth.read_text(encoding="utf-8")) if pth.exists() else None

    heroes_data = load_or_none(args.heroes) or []
    skills_data = load_or_none(args.skills) or []
    gear_data = load_or_none(args.gear)
    conquest_data = load_or_none(args.conquest_stats) or []
    expedition_data = load_or_none(args.expedition_stats) or []
    exclusive_skill_lookup = build_exclusive_skill_lookup(skills_data)
    gear_entries = list(iter_gear(gear_data))

    conquest_stats: dict[str, dict] = {}
    for entry in iter_entries(conquest_data):
        if not isinstance(entry, dict):
            continue
        hero_slug = slugify(
            entry.get("hero_id")
            or entry.get("hero")
            or entry.get("name")
            or entry.get("id")
            or ""
        )
        if not hero_slug:
            continue
        conquest_stats[hero_slug] = entry

    expedition_stats: dict[str, dict] = {}
    for entry in iter_entries(expedition_data):
        if not isinstance(entry, dict):
            continue
        hero_slug = slugify(
            entry.get("hero_id")
            or entry.get("hero")
            or entry.get("name")
            or entry.get("id")
            or ""
        )
        if not hero_slug:
            continue
        expedition_stats[hero_slug] = entry

    derived_stats: dict[str, tuple[int | None, int | None, int | None]] = {}
    for entry in gear_entries:
        hero_slug = slugify(
            entry.get("hero_id") or entry.get("hero") or entry.get("name") or ""
        )
        if not hero_slug:
            continue
        for _, level_data in iter_level_items(entry.get("levels")):
            atk = level_data.get("hero_attack") or level_data.get("attack")
            dfn = level_data.get("hero_defense") or level_data.get("defense")
            hp = level_data.get("hero_health") or level_data.get("health")
            if atk is None or dfn is None or hp is None:
                continue
            derived_stats[hero_slug] = (atk, dfn, hp)
            break

    # Build set of known hero slugs for validation
    hero_slugs = set()
    for h in iter_heroes(heroes_data):
        hero_slugs.add(h["id"])

    sql = []
    sql.append("BEGIN;")

    # Heroes + optional base stats
    for h in iter_heroes(heroes_data):
        slug = h["id"]
        name = h.get("name")
        rarity = normalize_rarity(h.get("rarity"))
        generation = h.get("generation")
        hclass = normalize_class(h.get("class"))
        image_path = (
            h.get("image_path") or h.get("portrait") or default_hero_image_path(slug)
        )

        sql.append(
            "INSERT INTO heroes (hero_id_slug, name, rarity, generation, class, image_path) "
            f"VALUES ({sql_str(slug)}, {sql_str(name)}, {sql_str(rarity)}, {coalesce_int(generation)}, {sql_str(hclass)}, {sql_str(image_path)}) "
            "ON CONFLICT (hero_id_slug) DO NOTHING;"
        )

        conquest_entry = conquest_stats.get(slug)
        if conquest_entry:
            base_atk = conquest_entry.get("attack")
            base_def = conquest_entry.get("defense")
            base_hp = conquest_entry.get("health")
        else:
            base = h.get("base_stats") or {}
            base_atk = h.get("base_attack", base.get("attack"))
            base_def = h.get("base_defense", base.get("defense"))
            base_hp = h.get("base_health", base.get("health"))
        if slug in derived_stats:
            derived_atk, derived_def, derived_hp = derived_stats[slug]
            if base_atk is None:
                base_atk = derived_atk
            if base_def is None:
                base_def = derived_def
            if base_hp is None:
                base_hp = derived_hp
        if base_atk is not None and base_def is not None and base_hp is not None:
            sql.append(
                "INSERT INTO hero_stats (hero_id, attack, defense, health) "
                f"SELECT id, {coalesce_int(base_atk)}, {coalesce_int(base_def)}, {coalesce_int(base_hp)} FROM heroes WHERE hero_id_slug = {sql_str(slug)} "
                "ON CONFLICT (hero_id) DO NOTHING;"
            )

    for slug, entry in expedition_stats.items():
        if hero_slugs and slug not in hero_slugs:
            continue
        troop_type = (
            entry.get("troop_type")
            or entry.get("bonus_type")
            or entry.get("class")
            or entry.get("type")
        )
        normalized_troop = normalize_class(troop_type)
        if not normalized_troop:
            continue
        attack_pct = entry.get("attack_pct")
        defense_pct = entry.get("defense_pct")
        if attack_pct is None or defense_pct is None:
            continue
        sql.append(
            "INSERT INTO hero_expedition_stats (hero_id, troop_type, attack_pct, defense_pct) "
            f"SELECT id, {sql_str(normalized_troop)}, {coalesce_decimal(attack_pct)}, {coalesce_decimal(defense_pct)} FROM heroes WHERE hero_id_slug = {sql_str(slug)} "
            "ON CONFLICT (hero_id) DO NOTHING;"
        )

    for hero_slug, s, bt in collect_skills(skills_data):
        if hero_slugs and hero_slug not in hero_slugs:
            # allow seeding skills even if hero missing; skip if strict
            pass
        s_name = s.get("name")
        if not s_name:
            continue
        s_type_raw = s.get("type")
        skill_type = normalize_skill_type(
            s_type_raw if s_type_raw not in ("Conquest", "Expedition", "Base") else None
        )
        desc = s.get("description")
        if skill_type == "Talent" or bt == "Base":
            icon_path = s.get("icon_path") or default_talent_icon_path(hero_slug)
        else:
            icon_path = s.get("icon_path") or default_skill_icon_path(hero_slug, s_name)

        sql.append(
            "INSERT INTO hero_skills (hero_id, name, skill_type, battle_type, description, icon_path) "
            f"SELECT id, {sql_str(s_name)}, {sql_str(skill_type)}, {sql_str(bt)}, {sql_str(desc)}, {sql_str(icon_path)} "
            f"FROM heroes WHERE hero_id_slug = {sql_str(hero_slug)} "
            "ON CONFLICT (hero_id, name) DO NOTHING;"
        )

        for lvl, eff in iter_level_items(s.get("levels")):
            sql.append(
                "INSERT INTO hero_skill_levels (skill_id, level, effects) "
                f"SELECT s.id, {coalesce_int(lvl)}, {sql_json(eff)} FROM hero_skills s "
                f"JOIN heroes h ON h.id = s.hero_id AND h.hero_id_slug = {sql_str(hero_slug)} "
                f"WHERE s.name = {sql_str(s_name)} "
                "ON CONFLICT (skill_id, level) DO NOTHING;"
            )

    # Exclusive gear (optional)
    for g in iter_gear(gear_data):
        hero_slug = slugify(g.get("hero_id") or g.get("hero") or g.get("name") or "")
        gear_name = g.get("name")
        if not gear_name:
            continue

        gear_image_path = g.get("image_path") or default_gear_image_path(gear_name)

        sql.append(
            "INSERT INTO hero_exclusive_gear (hero_id, name, image_path) "
            f"SELECT id, {sql_str(gear_name)}, {sql_str(gear_image_path)} FROM heroes "
            f"WHERE hero_id_slug = {sql_str(hero_slug)} "
            "ON CONFLICT (hero_id) DO NOTHING;"
        )

        levels = iter_level_items(g.get("levels"))

        for lvl, lv in levels:
            atk = (
                lv.get("attack")
                if lv.get("attack") is not None
                else lv.get("hero_attack")
            )
            dfn = (
                lv.get("defense")
                if lv.get("defense") is not None
                else lv.get("hero_defense")
            )
            hp = (
                lv.get("health")
                if lv.get("health") is not None
                else lv.get("hero_health")
            )
            leth = lv.get("lethality") or lv.get("troop_lethality_bonus")
            thp = lv.get("health_bonus") or lv.get("troop_health_bonus")

            conquest_effect = normalize_skill_effect(lv.get("skill_1"))
            expedition_effect = normalize_skill_effect(lv.get("skill_2"))

            sql.append(
                "INSERT INTO hero_exclusive_gear_levels (gear_id, level, hero_attack, hero_defense, hero_health, troop_lethality_bonus, troop_health_bonus, conquest_skill_effect, expedition_skill_effect) "
                f"SELECT g.id, {coalesce_int(lvl)}, {coalesce_int(atk)}, {coalesce_int(dfn)}, {coalesce_int(hp)}, "
                f"{sql_json(leth)}, {sql_json(thp)}, {sql_json(conquest_effect)}, {sql_json(expedition_effect)} "
                "FROM hero_exclusive_gear g "
                f"JOIN heroes h ON h.id = g.hero_id AND h.hero_id_slug = {sql_str(hero_slug)} "
                "ON CONFLICT (gear_id, level) DO NOTHING;"
            )

        conquest_skill_name = g.get("conquest_skill_name")
        expedition_skill_name = g.get("expedition_skill_name")

        if conquest_skill_name:
            sql.append(
                "INSERT INTO hero_exclusive_gear_skills (gear_id, skill_type, name, description) "
                f"SELECT g.id, 'Conquest', {sql_str(conquest_skill_name)}, {sql_str(g.get('conquest_skill_description'))} "
                "FROM hero_exclusive_gear g JOIN heroes h ON h.id = g.hero_id "
                f"WHERE h.hero_id_slug = {sql_str(hero_slug)} "
                "ON CONFLICT (gear_id, skill_type) DO NOTHING;"
            )
        if expedition_skill_name:
            sql.append(
                "INSERT INTO hero_exclusive_gear_skills (gear_id, skill_type, name, description) "
                f"SELECT g.id, 'Expedition', {sql_str(expedition_skill_name)}, {sql_str(g.get('expedition_skill_description'))} "
                "FROM hero_exclusive_gear g JOIN heroes h ON h.id = g.hero_id "
                f"WHERE h.hero_id_slug = {sql_str(hero_slug)} "
                "ON CONFLICT (gear_id, skill_type) DO NOTHING;"
            )

    sql.append("COMMIT;")

    out_path = Path("supabase/seed.sql")
    out_path.write_text("\n".join(sql), encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()
