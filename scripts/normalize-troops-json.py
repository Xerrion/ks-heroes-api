import json
from collections import defaultdict
from pathlib import Path


def normalize_troop_stats(input_path: str, output_path: str | None = None):
    """Normalize Kingshot troop stats into structure:
    troopType -> troopLevel -> tgLevel -> stats"""

    raw = json.loads(Path(input_path).read_text())
    data = raw["troop-stats"]

    normalized = {}

    for troop_type, entries in data.items():
        troop_dict = defaultdict(dict)

        for entry in entries:
            level = int(entry["Troop Level"])
            tg = int(entry["FC level"])  # FC is TG in Kingshot

            # Clean stats by removing meta keys
            stats = {
                k: v
                for k, v in entry.items()
                if k
                not in ("Troop Type", "Troop Level", "troop level name", "FC level")
            }

            troop_dict[level][tg] = stats

        # Sort numerical levels and TG levels
        normalized[troop_type] = {
            lvl: dict(sorted(tg_map.items()))
            for lvl, tg_map in sorted(troop_dict.items())
        }

    if output_path:
        Path(output_path).write_text(json.dumps(normalized, indent=2))
        print(f"Normalized troop stats written to {output_path}")

    return normalized


if __name__ == "__main__":
    input_file = "data/troop-stats.json"
    output_file = "data/troop-stats-normalized.json"

    result = normalize_troop_stats(input_file, output_file)
    print("Done. TG levels normalized.")
