# Troops API Documentation

## Endpoint

### GET `/troops` - Get Troops

Returns troop stats with flexible filtering and grouping options.

**Query Parameters:**

- `type` (optional): Filter by `Infantry`, `Cavalry`, or `Archer`
- `level` (optional): Exact troop level (1-11)
- `min_level` (optional, default: 1): Minimum troop level (1-11)
- `max_level` (optional, default: 10): Maximum troop level (1-11)
- `tg` (optional): Exact True Gold level (0-10)
- `min_tg` (optional, default: 0): Minimum True Gold level (0-10)
- `max_tg` (optional, default: 5): Maximum True Gold level (0-10)
- `group_by` (default: `type`): Group by `type` or `none` for flat list

**Parameter Logic:**

- Exact match parameters (`level`, `tg`) override range parameters when specified
- Range parameters (`min_level`, `max_level`, `min_tg`, `max_tg`) support filtering across ranges
- Use exact params for single configuration: `?type=infantry&level=11&tg=5`
- Use range params for multiple: `?min_level=8&max_level=10`

**Response Formats:**

#### Grouped by Type (Default)

`GET /troops` or `GET /troops?group_by=type`

```json
{
  "Infantry": [
    {
      "troop_level": 5,
      "true_gold_level": 2,
      "stats": {
        "attack": 7,
        "defense": 10,
        "health": 12,
        "lethality": 6,
        "power": 15,
        "load": 188,
        "speed": 11
      }
    }
  ],
  "Cavalry": [
    {
      "troop_level": 5,
      "true_gold_level": 2,
      "stats": {
        "attack": 14,
        "defense": 8,
        "health": 10,
        "lethality": 12,
        "power": 15,
        "load": 758,
        "speed": 14
      }
    }
  ],
  "Archer": []
}
```

#### Flat List

`GET /troops?group_by=none`

```json
[
  {
    "id": 1,
    "troop_type": "Infantry",
    "troop_level": 5,
    "true_gold_level": 2,
    "attack": 7,
    "defense": 10,
    "health": 12,
    "lethality": 6,
    "power": 15,
    "load": 188,
    "speed": 11,
    "created_at": "2025-11-13T11:32:31.727317+00:00",
    "updated_at": "2025-11-13T11:32:31.727317+00:00"
  }
]
```

## Example Usage

### Get all current troops (grouped by type)

```bash
curl http://localhost:8000/troops
```

### Get Infantry only (grouped)

```bash
curl "http://localhost:8000/troops?troop_type=Infantry"
```

### Get high-level troops with True Gold (flat list)

```bash
curl "http://localhost:8000/troops?min_level=8&min_tg=3&group_by=none"
```

### Get Helios troops (level 11)

```bash
curl "http://localhost:8000/troops?min_level=11&max_level=11"
```

### Get future True Gold tiers (6-10)

```bash
curl "http://localhost:8000/troops?min_tg=6&max_tg=10"
```

---

### GET `/troops/{type}/{level}` - Get Specific Troop Configuration

Returns stats for a specific troop type and level.

**Path Parameters:**

- `type`: `Infantry`, `Cavalry`, or `Archer`
- `level`: Troop level (1-11)

**Query Parameters:**

- `true_gold_level` (default: 0): True Gold level (0-10)

**Response:**

```json
{
  "id": 47,
  "troop_type": "Infantry",
  "troop_level": 5,
  "true_gold_level": 2,
  "attack": 7,
  "defense": 10,
  "health": 12,
  "lethality": 6,
  "power": 15,
  "load": 188,
  "speed": 11,
  "created_at": "2025-11-13T11:32:31.727317+00:00",
  "updated_at": "2025-11-13T11:32:31.727317+00:00"
}
```

## Example Usage

### Get Infantry level 5 with no True Gold

```bash
curl http://localhost:8000/troops/Infantry/5
```

## Design Notes

### Single Endpoint Philosophy

This API uses **one endpoint** (`GET /troops`) for all queries instead of separate endpoints for lists vs single items. Benefits:

1. **Simpler API surface**: Fewer endpoints to learn and maintain
2. **Flexible filtering**: Exact match OR range queries with same endpoint
3. **Better caching**: Query params are easier to cache and vary
4. **Consistent patterns**: Same structure for all data APIs (VIP, Troops, etc.)

### Parameter Naming

Short, clear names for better developer experience:

- `type` instead of `troop_type`
- `level` instead of `troop_level`
- `tg` instead of `true_gold_level`

### Grouped by Default

1. **Better UX**: Most consumers want to compare troop types side-by-side
2. **Smaller payloads**: No repeated `troop_type` field in every object
3. **Easier client-side consumption**: Object structure matches UI layouts
4. **Flexible**: Can still get flat list with `group_by=none`

### True Gold Levels

The API stores TG levels 0-10 for future-proofing:

- **TG 0-5**: Currently in game
- **TG 6-10**: Future content (stored but filtered by default)

Consumers can access future TG tiers by setting `max_tg=10` or `tg=<tier>`.

### Troop Stats are Flat Numbers

True Gold bonuses are **additive flat numbers**, not percentages. The stats returned are the exact final values shown in-game for that troop configuration.

Example: Infantry L5 TG2 has attack=7 (not base=5 + 40% bonus).

Consumers can access future TG tiers by setting `max_tg=10`.

### Troop Stats are Flat Numbers

True Gold bonuses are **additive flat numbers**, not percentages. The stats returned are the exact final values shown in-game for that troop configuration.

Example: Infantry L5 TG2 has attack=7 (not base=5 + 40% bonus).
