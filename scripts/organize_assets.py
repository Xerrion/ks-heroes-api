"""Organize hero, talent, gear, and skill images into the canonical layout."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

try:  # Pillow is only needed when conversion happens
    from PIL import Image
except ImportError:  # pragma: no cover - optional dependency
    Image = None  # type: ignore

try:  # thefuzz improves scoring when present
    from thefuzz import fuzz
except ImportError:  # pragma: no cover - optional dependency
    fuzz = None  # type: ignore

SUPPORTED_SUFFIXES = {".webp", ".png", ".jpg", ".jpeg", ".svg"}
_SIZE_SUFFIX_RE = re.compile(r"-(\d+)(x\d+)?$", re.IGNORECASE)
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str | None) -> str:
    value = (value or "").strip().lower()
    return _SLUG_RE.sub("-", value).strip("-")


def tokenize(*values: str | None) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        if not value:
            continue
        for token in slugify(value).split("-"):
            if token:
                tokens.add(token)
    return tokens


def strip_size_suffix(stem: str) -> str:
    return _SIZE_SUFFIX_RE.sub("", stem)


def _load_json(path: Path) -> object:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - data error
        raise SystemExit(f"Failed to parse {path}: {exc}")


def _iter_collection(obj: object) -> Iterable[dict]:
    if isinstance(obj, dict):
        for value in obj.values():
            if isinstance(value, dict):
                yield value
    elif isinstance(obj, list):
        for value in obj:
            if isinstance(value, dict):
                yield value


def _hero_lookup(raw: object) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for entry in _iter_collection(raw) or []:
        hero_id = slugify(entry.get("id") or entry.get("hero_id") or entry.get("name"))
        if hero_id:
            lookup[hero_id] = entry.get("name") or hero_id.replace("-", " ").title()
    return lookup


def _skills_catalog(raw: object) -> dict[str, dict[str, Sequence[str]]]:
    catalog: dict[str, dict[str, Sequence[str]]] = {}
    for entry in _iter_collection(raw) or []:
        hero_id = slugify(
            entry.get("hero_id") or entry.get("hero") or entry.get("name")
        )
        if not hero_id:
            continue
        conquest = [
            s["name"] for s in entry.get("conquest_skills", []) if s.get("name")
        ]
        expedition = [
            s["name"] for s in entry.get("expedition_skills", []) if s.get("name")
        ]
        exclusive = [
            s["name"] for s in entry.get("exclusive_skills", []) if s.get("name")
        ]
        talent_name = None
        talent = entry.get("talent")
        if isinstance(talent, dict):
            talent_name = talent.get("name")
        catalog[hero_id] = {
            "conquest": tuple(conquest),
            "expedition": tuple(expedition),
            "exclusive": tuple(exclusive),
            "talent": (talent_name,) if talent_name else tuple(),
        }
    return catalog


def _exclusive_gear(raw: object) -> list[dict]:
    return list(_iter_collection(raw) or [])


@dataclass(slots=True)
class AssetTarget:
    dest_base: Path
    slug: str
    tokens: set[str]
    category: str
    description: str
    hero_id: str | None = None
    assigned_source: Path | None = field(default=None, init=False)

    def score(
        self,
        candidate_slug: str,
        candidate_tokens: set[str],
        known_hero_ids: set[str],
    ) -> float:
        if not candidate_slug or candidate_slug == "asset":
            return 0.0

        hero_tokens = candidate_tokens & known_hero_ids
        if hero_tokens and self.hero_id and self.hero_id not in hero_tokens:
            return 0.0
        if "talent" in candidate_tokens and self.category != "talent":
            return 0.0

        score = 0.0
        if candidate_slug == self.slug:
            score = 1.0
        elif self.slug and self.slug in candidate_slug:
            score = 0.85

        overlap = len(candidate_tokens & self.tokens)
        if self.tokens:
            score = max(score, overlap / len(self.tokens))

        if fuzz is not None and self.slug:
            score = max(score, fuzz.token_sort_ratio(candidate_slug, self.slug) / 100.0)

        if self.hero_id and self.hero_id in candidate_tokens:
            score = min(1.0, score + 0.2)
        if self.category == "talent" and "talent" in candidate_tokens:
            score = min(1.0, score + 0.2)
        if self.category.startswith("exclusive") and "exclusive" in candidate_tokens:
            score = min(1.0, score + 0.1)
        if self.category.startswith("skill") and "skill" in candidate_tokens:
            score = min(1.0, score + 0.1)

        return score

    @property
    def dest_default(self) -> Path:
        return self.dest_base.with_suffix(".png")


def build_asset_targets(data_dir: Path) -> tuple[list[AssetTarget], set[str]]:
    data_dir = Path(data_dir)
    heroes_raw = _load_json(data_dir / "heroes.json") or []
    skills_raw = _load_json(data_dir / "hero_skills.json") or []
    gear_raw = _load_json(data_dir / "exclusive_gear.json") or []

    hero_lookup = _hero_lookup(heroes_raw)
    skills_catalog = _skills_catalog(skills_raw)
    gear_entries = _exclusive_gear(gear_raw)

    targets: list[AssetTarget] = []
    seen_destinations: set[Path] = set()
    hero_ids: set[str] = set(hero_lookup.keys())

    def add_target(
        dest: Path,
        slug_source: str,
        tokens: Iterable[str],
        *,
        category: str,
        description: str,
        hero_id: str | None = None,
    ) -> None:
        dest_base = dest.with_suffix("")
        slug = slugify(slug_source)
        target_tokens = tokenize(*tokens)
        if not slug:
            return
        target = AssetTarget(
            dest_base=dest_base,
            slug=slug,
            tokens=target_tokens,
            category=category,
            description=description,
            hero_id=hero_id,
        )
        if dest_base in seen_destinations:
            return
        seen_destinations.add(dest_base)
        targets.append(target)
        if hero_id:
            hero_ids.add(hero_id)

    for hero_id, hero_name in hero_lookup.items():
        add_target(
            Path("heroes") / f"{hero_id}.png",
            hero_id,
            (hero_id, hero_name, "hero", "portrait"),
            category="hero",
            description=f"Hero portrait for {hero_name}",
            hero_id=hero_id,
        )

    for hero_id, details in skills_catalog.items():
        talent_names = details.get("talent", ())
        for talent_name in talent_names:
            add_target(
                Path("talents") / f"{hero_id}.png",
                talent_name,
                (talent_name, hero_id, "talent"),
                category="talent",
                description=f"Talent icon for {hero_lookup.get(hero_id, hero_id)}",
                hero_id=hero_id,
            )

        for skill_name in details.get("conquest", ()):  # hero conquest skills
            add_target(
                Path("skills") / hero_id / f"{slugify(skill_name)}.png",
                skill_name,
                (skill_name, hero_id, "skill", "conquest"),
                category="skill-conquest",
                description=f"Conquest skill '{skill_name}' for {hero_id}",
                hero_id=hero_id,
            )

        for skill_name in details.get("expedition", ()):
            add_target(
                Path("skills") / hero_id / f"{slugify(skill_name)}.png",
                skill_name,
                (skill_name, hero_id, "skill", "expedition"),
                category="skill-expedition",
                description=f"Expedition skill '{skill_name}' for {hero_id}",
                hero_id=hero_id,
            )

        for skill_name in details.get("exclusive", ()):  # duplicates avoided later
            add_target(
                Path("exclusive/skills") / hero_id / f"{slugify(skill_name)}.png",
                skill_name,
                (skill_name, hero_id, "exclusive", "skill"),
                category="exclusive-skill",
                description=f"Exclusive skill '{skill_name}' for {hero_id}",
                hero_id=hero_id,
            )

    for entry in gear_entries:
        hero_id = slugify(
            entry.get("hero_id") or entry.get("hero") or entry.get("name")
        )
        gear_name = entry.get("name")
        if not hero_id or not gear_name:
            continue

        add_target(
            Path("exclusive/gear") / f"{slugify(gear_name)}.png",
            gear_name,
            (gear_name, hero_id, "gear", "exclusive"),
            category="exclusive-gear",
            description=f"Exclusive gear '{gear_name}' for {hero_lookup.get(hero_id, hero_id)}",
            hero_id=hero_id,
        )

        conquest_skill = entry.get("conquest_skill_name")
        if conquest_skill:
            add_target(
                Path("exclusive/skills") / hero_id / f"{slugify(conquest_skill)}.png",
                conquest_skill,
                (conquest_skill, hero_id, "exclusive", "conquest", "skill"),
                category="exclusive-skill",
                description=f"Exclusive conquest skill '{conquest_skill}'",
                hero_id=hero_id,
            )

        expedition_skill = entry.get("expedition_skill_name")
        if expedition_skill:
            add_target(
                Path("exclusive/skills") / hero_id / f"{slugify(expedition_skill)}.png",
                expedition_skill,
                (expedition_skill, hero_id, "exclusive", "expedition", "skill"),
                category="exclusive-skill",
                description=f"Exclusive expedition skill '{expedition_skill}'",
                hero_id=hero_id,
            )

    return targets, hero_ids


def discover_candidate_files(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        return []
    return sorted(
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )


def determine_destination(
    target: AssetTarget,
    output_dir: Path,
    source_suffix: str,
    convert_format: str,
) -> Path:
    if convert_format == "png":
        return output_dir / target.dest_base.with_suffix(".png")
    return output_dir / target.dest_base.with_suffix(source_suffix.lower())


def ensure_pillow_available() -> None:
    if Image is None:
        raise RuntimeError(
            "Pillow is required for image conversion. Install it with `uv pip install Pillow`."
        )


def auto_crop_image(image):
    if image.mode != "RGBA":
        working = image.convert("RGBA")
    else:
        working = image
    bbox = working.getbbox()
    return image.crop(bbox) if bbox else image


def resize_image(image, max_size: int = 300):
    if image.width <= max_size and image.height <= max_size:
        return image
    ratio = min(max_size / image.width, max_size / image.height)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    try:
        resample = Image.Resampling.LANCZOS  # type: ignore[attr-defined]
    except AttributeError:
        resample = Image.LANCZOS  # type: ignore[attr-defined]
    return image.resize(new_size, resample)


def convert_and_write(
    source: Path,
    destination: Path,
    *,
    convert_format: str,
    overwrite: bool,
    keep_source: bool,
    dry_run: bool,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not overwrite:
        raise FileExistsError(destination)
    if dry_run:
        return

    ensure_pillow_available()
    assert Image is not None  # for type checkers
    with Image.open(source) as image:
        processed = resize_image(auto_crop_image(image))
        if convert_format == "png":
            processed.save(destination, format="PNG", optimize=True)
        else:
            processed.save(destination, optimize=True)
    if not keep_source and source != destination:
        source.unlink()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Organize hero & skill assets")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("assets/images"),
        help="Directory where raw images are staged (default: assets/images)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("assets/images"),
        help="Destination base directory (default: assets/images)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory containing JSON metadata (default: data)",
    )
    parser.add_argument(
        "--convert-format",
        choices=["png", "keep"],
        default="png",
        help="Convert images to this format (default: png).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite destination files when they already exist.",
    )
    parser.add_argument(
        "--keep-source",
        action="store_true",
        help="Retain the source file after conversion.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the operations without writing files.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.70,
        help="Minimum matching score to accept an assignment.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print additional matching details.",
    )
    return parser.parse_args()


def organize_assets(args: argparse.Namespace) -> None:
    targets, hero_ids = build_asset_targets(args.data_dir)
    candidates = discover_candidate_files(args.input_dir)
    if not candidates:
        print("No candidate image files found.")
        return

    assigned: list[tuple[Path, Path, AssetTarget, float]] = []
    unmatched: list[Path] = []
    processed_slugs: set[str] = set()

    for source in candidates:
        base_stem = strip_size_suffix(source.stem)
        candidate_slug = slugify(base_stem)
        candidate_tokens = tokenize(candidate_slug)
        if candidate_slug in processed_slugs:
            print(f"⏭️  Skipping {source.name} (duplicate slug: {candidate_slug})")
            continue
        processed_slugs.add(candidate_slug)

        best_target: AssetTarget | None = None
        best_score = 0.0
        for target in targets:
            if target.assigned_source is not None:
                continue
            score = target.score(candidate_slug, candidate_tokens, hero_ids)
            if score > best_score:
                best_score = score
                best_target = target

        if best_target and best_score >= args.min_score:
            destination = determine_destination(
                best_target,
                args.output_dir,
                source.suffix,
                args.convert_format,
            )
            try:
                convert_and_write(
                    source,
                    destination,
                    convert_format=args.convert_format,
                    overwrite=args.overwrite,
                    keep_source=args.keep_source,
                    dry_run=args.dry_run,
                )
            except FileExistsError:
                print(
                    f"⚠️  Skipping {source.name} -> {destination} (already exists; use --overwrite)"
                )
                unmatched.append(source)
                continue

            best_target.assigned_source = source
            assigned.append((source, destination, best_target, best_score))
            note = " (dry run)" if args.dry_run else ""
            print(
                f"✅ {source.name} -> {destination}{note}\n"
                f"    category: {best_target.category} | {best_target.description}\n"
                f"    match score: {best_score:.2f}"
                + (f" | slug: {candidate_slug}" if args.verbose else "")
            )
        else:
            unmatched.append(source)
            print(f"❓ Could not match {source.name} (slug: {candidate_slug})")

    print("\nSummary")
    print("-------")
    print(f"Matched: {len(assigned)}")
    print(f"Unmatched: {len(unmatched)}")
    for path in unmatched:
        print(f" - {path.name}")


def main() -> None:
    organize_assets(parse_args())


if __name__ == "__main__":
    main()
