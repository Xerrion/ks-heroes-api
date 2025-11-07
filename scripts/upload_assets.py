"""Upload curated asset images to Supabase Storage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db.storage import ensure_bucket_exists, upload_directory

DEFAULT_PATTERNS: tuple[str, ...] = ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.svg")


def _normalize_patterns(patterns: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(patterns) if patterns else DEFAULT_PATTERNS


def _collect_matches(
    directory: Path, patterns: Iterable[str], prefix: str
) -> list[tuple[Path, str]]:
    directory = directory.resolve()
    if not directory.exists() or not directory.is_dir():
        raise FileNotFoundError(
            f"Directory {directory} does not exist or is not a directory"
        )

    seen: set[Path] = set()
    matches: list[tuple[Path, str]] = []
    prefix_path = Path(prefix) if prefix else None

    for pattern in patterns:
        for file_path in directory.rglob(pattern):
            if not file_path.is_file() or file_path in seen:
                continue
            relative = file_path.relative_to(directory)
            storage_path = (
                prefix_path / relative if prefix_path else relative
            ).as_posix()
            matches.append((file_path, storage_path))
            seen.add(file_path)
    matches.sort(key=lambda item: item[1])
    return matches


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload asset images to Supabase Storage"
    )
    parser.add_argument(
        "source_dir",
        type=Path,
        nargs="?",
        default=Path("assets/images"),
        help="Directory containing image assets (default: assets/images)",
    )
    parser.add_argument(
        "--bucket",
        help="Override the target bucket name (defaults to SUPABASE_STORAGE_BUCKET)",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Optional key prefix inside the bucket (e.g. heroes/, skills/)",
    )
    parser.add_argument(
        "--pattern",
        dest="patterns",
        action="append",
        help="Glob pattern(s) to include (default: *.png, *.jpg, *.jpeg, *.webp, *.svg)",
    )
    parser.add_argument(
        "--no-upsert",
        dest="upsert",
        action="store_false",
        help="Disable overwriting existing files",
    )
    parser.add_argument(
        "--cache",
        dest="cache_control",
        type=int,
        default=3600,
        help="Cache-Control max-age in seconds",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List the files that would be uploaded without performing uploads",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    patterns = _normalize_patterns(args.patterns)
    matches = _collect_matches(args.source_dir, patterns, args.prefix)

    if not matches:
        print("No files matched the provided patterns.")
        return

    print(f"Found {len(matches)} files ready for upload.")
    for file_path, storage_key in matches[:10]:
        print(f" - {storage_key} ({file_path})")
    if len(matches) > 10:
        print("... (remaining files omitted)")

    if args.dry_run:
        print("Dry run complete; no files uploaded.")
        return

    ensure_bucket_exists(bucket=args.bucket)
    urls = upload_directory(
        directory=args.source_dir,
        bucket=args.bucket,
        prefix=args.prefix,
        patterns=patterns,
        cache_control=args.cache_control,
        upsert=args.upsert,
    )

    print(f"Uploaded {len(urls)} files to bucket '{args.bucket or 'default'}'.")
    for url in urls[:10]:
        print(f" - {url}")
    if len(urls) > 10:
        print("... (remaining URLs omitted)")


if __name__ == "__main__":
    main()
