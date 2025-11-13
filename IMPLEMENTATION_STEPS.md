# VIP & Troops Implementation - Next Steps

## ✅ Files Created

### Repositories

- ✅ `src/db/repositories/vip.py` - VIP data access layer
- ✅ `src/db/repositories/troops.py` - Troops data access layer

### Routes

- ✅ `src/routes/vip/get_all.py` - GET /vip (with filters)
- ✅ `src/routes/vip/get_by_level.py` - GET /vip/{level}
- ✅ `src/routes/troops/get_all.py` - GET /troops (with filters)
- ✅ `src/routes/troops/get_by_configuration.py` - GET /troops/{type}/{level}

### Configuration

- ✅ `src/dependencies.py` - Added `get_vip_repository()` and `get_troops_repository()`
- ✅ `src/main.py` - Registered VIP and Troops routes

---

## 🔨 Manual Steps Required

### 1. Apply Database Migrations

```bash
# Navigate to project directory
cd /Users/lasn/Projects/Python/ks-heroes-api

# Apply all pending migrations
uv run supabase migration up
```

**Expected migrations to apply:**

- `20251113000003_add_vip_system.sql`
- `20251113000004_add_troops_system.sql`

---

### 2. Generate and Load Seed Data

```bash
# Generate seed SQL from JSON data
uv run python scripts/generate_seed_sql.py

# This will create/update: supabase/seed.sql
```

**Check the generated SQL includes:**

- VIP levels (12 entries)
- Troops data (infantry, cavalry, archer with all TG levels)

---

### 3. Apply Seed Data

```bash
# Reset database and apply seed data
uv run supabase db reset

# This will:
# 1. Drop all tables
# 2. Re-run all migrations
# 3. Load seed.sql data
```

---

### 4. Start Development Server

```bash
# Start FastAPI development server
uv run fastapi dev src/main.py
```

The server will start at `http://localhost:8000`

---

### 5. Test the API

#### Open Swagger UI

```bash
open http://localhost:8000/docs
```

#### Test VIP Endpoints

**Get all VIP levels:**

```bash
curl http://localhost:8000/vip
```

**Get all VIP levels 10-12:**

```bash
curl "http://localhost:8000/vip?min_level=10&max_level=12"
```

**Get VIP level 12:**

```bash
curl http://localhost:8000/vip/12
```

#### Test Troops Endpoints

**Get all troops (default: grouped by type, levels 1-10, TG 0-5):**

```bash
curl http://localhost:8000/troops
```

Expected response (grouped):

```json
{
  "Infantry": [
    {
      "troop_level": 1,
      "true_gold_level": 0,
      "stats": {
        "attack": 1,
        "defense": 4,
        "health": 6,
        "lethality": 1,
        "power": 3,
        "load": 108,
        "speed": 11
      }
    }
  ],
  "Cavalry": [...],
  "Archer": [...]
}
```

**Get all troops as flat list:**

```bash
curl "http://localhost:8000/troops?group_by=none"
```

**Get Infantry troops only (grouped):**

```bash
curl "http://localhost:8000/troops?type=Infantry"
```

**Get all Cavalry with True Gold 0-10 (grouped):**

```bash
curl "http://localhost:8000/troops?type=Cavalry&max_tg=10"
```

**Get Helios level troops (level 11, grouped):**

```bash
curl "http://localhost:8000/troops?level=11"
```

**Get specific configuration (Cavalry level 10, TG 5):**

```bash
curl "http://localhost:8000/troops?type=Cavalry&level=10&tg=5"
```

**Get Archer level 1 with no True Gold:**

```bash
curl "http://localhost:8000/troops?type=Archer&level=1&tg=0"
```

---

## 📊 Expected API Responses

### VIP Level Response

```json
{
  "level": 12,
  "resource_production_speed_pct": "24.00",
  "storehouse_capacity": 1100000,
  "construction_speed_pct": "20.00",
  "formations": 2,
  "march_queue": 1,
  "squads_attack_pct": "16.00",
  "squads_defense_pct": "16.00",
  "squads_health_pct": "16.00",
  "squads_lethality_pct": "16.00",
  "custom_avatar_upload_cooldown_hours": -48,
  "created_at": "2025-11-13T...",
  "updated_at": "2025-11-13T..."
}
```

### Troop Response (Grouped by Type - Default)

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
  "Cavalry": [],
  "Archer": []
}
```

### Troop Response (Flat List - group_by=none)

```json
[
  {
    "id": 1,
    "troop_type": "Cavalry",
    "troop_level": 10,
    "true_gold_level": 5,
    "attack": 20,
    "defense": 26,
    "health": 30,
    "lethality": 20,
    "power": 132,
    "load": 758,
    "speed": 14,
    "created_at": "2025-11-13T...",
    "updated_at": "2025-11-13T..."
  }
]
```

---

## ✅ Verification Checklist

After running all steps, verify:

- [ ] Database migrations applied successfully
- [ ] Seed data loaded (check table counts)
  - `SELECT COUNT(*) FROM vip_levels;` → Should be 12
  - `SELECT COUNT(*) FROM troops;` → Should be 363 (3 types × 11 levels × 11 TG levels)
- [ ] Server starts without errors
- [ ] Swagger UI accessible at `/docs`
- [ ] VIP endpoints return data
- [ ] Troops endpoints return data
- [ ] Filters work correctly (test with different parameters)
- [ ] 404 errors for non-existent resources

---

## 🐛 Troubleshooting

### Migration Errors

```bash
# If migrations fail, check migration history
uv run supabase migration list

# Repair if needed
uv run supabase migration repair --status applied <version>
```

### Seed Data Issues

```bash
# Check generated seed.sql
cat supabase/seed.sql | grep "INSERT INTO vip_levels"
cat supabase/seed.sql | grep "INSERT INTO troops"
```

### Import Errors

```bash
# If you see import errors, regenerate lock file
uv lock
```

---

## 🎯 Next Steps After Testing

Once VIP and Troops are working:

1. **Write integration tests**
2. **Update README.md** with new endpoints
3. **Consider adding:**
   - Caching (Redis/in-memory)
   - Rate limiting
   - API versioning (/v1/vip)
   - CSV/JSON export endpoints
4. **Prepare for deployment**

---

## 📝 Notes

- Default filters are set to match current game state (TG 0-5, levels 1-10)
- Data consumers can override filters to access future content
- All endpoints are read-only (GET only)
- Responses use Pydantic for automatic validation
- Database uses proper indexes for efficient queries
