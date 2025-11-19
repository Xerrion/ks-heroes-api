"""Organize troop icon assets into the canonical layout."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

try:  # Pillow is optional; only required when converting formats
    from PIL import Image  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    Image = None  # type: ignore[assignment]

if TYPE_CHECKING:  # pragma: no cover - typing helpers only
    from PIL import Image as PILImage  # type: ignore[import-not-found]

SUPPORTED_SUFFIXES = {".webp", ".png", ".jpg", ".jpeg", ".svg"}
_SLUG_RE = re.compile(r"[^a-z0-9]+")
_SIZE_SUFFIX_RE = re.compile(r"[-_](\d+)(x\d+)?$", re.IGNORECASE)

TROOP_TYPE_ALIASES: dict[str, str] = {
    "inf": "infantry",
    "infantry": "infantry",
    "infantryman": "infantry",
    "infantrymen": "infantry",
    "infantries": "infantry",
    "cav": "cavalry",
    "cavalry": "cavalry",
    "cavalries": "cavalry",
    "cavalier": "cavalry",
    "arch": "archer",
    "archer": "archer",
    "archers": "archer",
}


def slugify(value: str | None) -> str:
    value = (value or "").strip().lower()
    return _SLUG_RE.sub("-", value).strip("-")


def strip_size_suffix(stem: str) -> str:
    return _SIZE_SUFFIX_RE.sub("", stem)


def tokenize(text: str) -> set[str]:
    tokens = set()
    for token in slugify(text).split("-"):
        if not token:
            continue
        tokens.add(token)
        alias = TROOP_TYPE_ALIASES.get(token)
        if alias:
            tokens.add(alias)
    return tokens


@dataclass(slots=True)
class TroopTarget:
    troop_type: str
    level: int
    dest_base: Path
    tokens: set[str]
    slug: str

    def destination(self, output_dir: Path, convert_format: str) -> Path:
        suffix = ".png"
        if convert_format == "webp":
            suffix = ".webp"
        elif convert_format == "keep":
            # Destination inherits whatever suffix was used when the file was matched.
            # Caller is responsible for appending the original suffix.
            return (output_dir / self.dest_base).with_suffix("")
        return (output_dir / self.dest_base).with_suffix(suffix)


def build_targets(data_file: Path) -> list[TroopTarget]:
    payload = json.loads(data_file.read_text(encoding="utf-8"))
    targets: list[TroopTarget] = []

    for troop_type, levels in payload.items():
        raw_type = TROOP_TYPE_ALIASES.get(troop_type, troop_type) or troop_type
        normalized_type = str(raw_type).lower()
        if not isinstance(levels, dict):
            continue

        seen_levels: set[int] = set()
        for level_str in levels.keys():
            try:
                level = int(level_str)
            except (TypeError, ValueError):
                continue
            if level in seen_levels:
                continue
            seen_levels.add(level)

            slug = f"{normalized_type}-{level}"
            tokens = {
                normalized_type,
                str(level),
                f"t{level}",
                f"tier{level}",
                f"lvl{level}",
                f"lv{level}",
                f"{normalized_type}{level}",
            }
            dest_base = Path("troops") / f"{normalized_type}_{level}"
            targets.append(
                TroopTarget(
                    troop_type=normalized_type,
                    level=level,
                    dest_base=dest_base,
                    tokens=tokens,
                    slug=slug,
                )
            )

    return targets


def discover_candidate_files(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        return []
    matches: list[Path] = []
    for path in input_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            matches.append(path)
    return sorted(matches)


def _score_target(
    target: TroopTarget, candidate_slug: str, candidate_tokens: set[str]
) -> float:
    if candidate_slug == target.slug:
        return 1.0

    type_match = any(
        token in candidate_tokens
        for token in [target.troop_type, target.troop_type.rstrip("y")]
    )
    level_tokens = {
        str(target.level),
        f"{target.level:02d}",
        f"t{target.level}",
        f"tier{target.level}",
        f"lvl{target.level}",
        f"lv{target.level}",
    }
    level_match = any(token in candidate_tokens for token in level_tokens)

    score = 0.0
    if type_match:
        score += 0.6
    if level_match:
        score += 0.35
    overlap = len(target.tokens & candidate_tokens)
    if target.tokens:
        score = max(score, overlap / len(target.tokens))

    if type_match and level_match:
        score = max(score, 0.95)
    return score


def ensure_pillow_available() -> None:
    if Image is None:
        raise RuntimeError(
            "Pillow is required for image conversion. Install it with `uv pip install Pillow`."
        )


def copy_or_convert(
    source: Path,
    destination: Path,
    *,
    convert_format: str,
    overwrite: bool,
    dry_run: bool,
) -> None:
    if convert_format == "keep":
        suffix = source.suffix.lower() if source.suffix else ""
        destination = destination.with_suffix(suffix)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not overwrite:
        raise FileExistsError(destination)
    if dry_run:
        return

    if convert_format == "keep":
        shutil.copy2(source, destination)
        return

    if convert_format not in {"png", "webp"}:
        shutil.copy2(source, destination)
        return

    if source.suffix.lower() == f".{convert_format}":
        shutil.copy2(source, destination)
        return

    ensure_pillow_available()
    assert Image is not None  # for type checking
    with Image.open(source) as image:
        if convert_format == "png":
            image.convert("RGBA").save(destination, format="PNG", optimize=True)
        else:
            image.convert("RGBA").save(
                destination,
                format="WEBP",
                method=6,
                quality=90,
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Organize troop icon assets.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("assets/images/troops/raw"),
        help="Directory containing raw troop images (default: assets/images/troops/raw).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("assets/images"),
        help="Destination base directory (default: assets/images).",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=Path("data/troop-stats.json"),
        help="JSON file containing troop metadata (default: data/troop-stats.json).",
    )
    parser.add_argument(
        "--convert-format",
        choices=["png", "webp", "keep"],
        default="png",
        help="Convert assets to this format (default: png).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite destination files if they already exist.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview operations without writing files.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.8,
        help="Minimum confidence score to accept a match (default: 0.8).",
    )
    return parser.parse_args()


def organize_troop_assets(args: argparse.Namespace) -> None:
    if not args.data_file.exists():
        raise FileNotFoundError(f"Data file not found: {args.data_file}")

    targets = build_targets(args.data_file)
    if not targets:
        print("No troop definitions found in the data file.")
        return

    candidates = discover_candidate_files(args.input_dir)
    if not candidates:
        print("No candidate troop images found.")
        return

    assigned = 0
    unmatched: list[Path] = []
    used_targets: set[Path] = set()

    for source in candidates:
        base_stem = strip_size_suffix(source.stem)
        candidate_slug = slugify(base_stem)
        candidate_tokens = tokenize(base_stem)
        if not candidate_tokens:
            unmatched.append(source)
            print(f"❓ Could not parse tokens for {source.name}")
            continue

        best_target: TroopTarget | None = None
        best_score = 0.0
        for target in targets:
            destination = (args.output_dir / target.dest_base).with_suffix(".png")
            if destination in used_targets and not args.overwrite:
                continue
            score = _score_target(target, candidate_slug, candidate_tokens)
            if score > best_score:
                best_score = score
                best_target = target

        if not best_target or best_score < args.min_score:
            unmatched.append(source)
            print(f"❌ No confident match for {source.name} (score={best_score:.2f})")
            continue

        destination = best_target.destination(args.output_dir, args.convert_format)
        if args.convert_format == "keep":
            destination = destination.with_suffix(source.suffix.lower())

        try:
            copy_or_convert(
                source,
                destination,
                convert_format=args.convert_format,
                overwrite=args.overwrite,
                dry_run=args.dry_run,
            )
        except FileExistsError:
            unmatched.append(source)
            print(
                f"⚠️  Skipping {source.name} -> {destination} "
                "(already exists; pass --overwrite to replace)"
            )
            continue

        used_targets.add(destination)
        assigned += 1
        note = " (dry run)" if args.dry_run else ""
        print(
            f"✅ {source.name} -> {destination}{note} "
            f"(type={best_target.troop_type}, level={best_target.level}, score={best_score:.2f})"
        )

    print("\nSummary")
    print("-------")
    print(f"Assigned: {assigned}")
    print(f"Unmatched: {len(unmatched)}")
    for path in unmatched:
        print(f" - {path.name}")


def main() -> None:
    organize_troop_assets(parse_args())


if __name__ == "__main__":
    main()
