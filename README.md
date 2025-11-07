# ⚔️ Kingshot Hero API

A structured, queryable API for **Kingshot hero data**, built with Supabase and designed to power external tools, battle simulators, and analytics platforms.

This project focuses **only on the data layer** — collecting, normalizing, and serving hero stats, skills, expedition bonuses, and exclusive gear.  
**Battle simulations will be a separate project that consumes this API.**

---

## 🎯 Purpose

Hero data in Kingshot is fragmented, inconsistent, and not built for automation.  
This API solves that by providing:

- ✅ A clean, normalized database of heroes, skills, stats, and gear
- ✅ Built using Supabase (PostgreSQL + RPC endpoints)
- ✅ JSON responses designed to be consumed by simulators, bots, or web tools
- ❌ No battle logic or damage formulas here — that's for a separate simulator project

---

## 🏗️ Architecture

### ✅ Database Schema (Supabase)

| Table                        | Purpose                                                      |
| ---------------------------- | ------------------------------------------------------------ |
| `heroes`                     | Core identity (name, class, rarity, generation, slug)        |
| `hero_conquest_stats`        | Base hero attack/defense/health                              |
| `hero_expedition_stats`      | Expedition troop bonuses (attack/defense/health/lethality %) |
| `hero_skills`                | Skills + classification: `Base`, `Conquest`, or `Expedition` |
| `hero_skill_levels`          | Level-based scaling for each skill (Lv1–5)                   |
| `hero_exclusive_gear`        | Exclusive hero gear                                          |
| `hero_exclusive_gear_levels` | Gear stats for levels 1–10                                   |
| `hero_exclusive_gear_skills` | Gear-based Conquest/Expedition skill upgrades                |

### ✅ Example RPC

```sql
select api_get_hero('marlin');
```

Returns structured JSON:

```json
{
  "hero_id": "marlin",
  "name": "Marlin",
  "class": "Archer",
  "base_stats": { "attack": 1752, "defense": 2220, "health": 10822 },
  "expedition_stats": { "attack_pct": 240.19, "defense_pct": 240.19 },
  "skills": {
    "base": [],
    "conquest": [],
    "expedition": []
  },
  "exclusive_gear": {}
}
```

---

## 🚀 Who Is This For?

This API is built for:

- ⚙️ Developers creating battle simulators
- 📊 Analysts researching game mechanics
- 🛡️ Alliance leaders building strategy tools or dashboards
- 🌐 Websites/apps showing hero stats and skill info

---

## ✅ This API Does NOT Include

| ❌ Not Included               | ✅ Instead                          |
| ----------------------------- | ----------------------------------- |
| No combat simulator           | A separate project will handle that |
| No troop damage/kill formulas | This API only provides data         |
| No hero “power” calculations  | Only raw stats and skills           |
| No GUI or frontend            | This is backend-first               |

---

## 🛠️ Setup

```bash
git clone <repo-url>
cd kingshot-hero-api
uv pip install -e .
cp .env.example .env    # add Supabase credentials
```

Run database migrations:

```bash
supabase db reset
```

---

## ✅ Current Status

| Status | Feature                                       |
| ------ | --------------------------------------------- |
| ✅     | Database schema complete                      |
| ✅     | Supabase migrations written                   |
| ✅     | RPC: `api_get_hero(slug)` implemented         |
| 🔄     | JSON → database seeding in progress           |
| 🔄     | Hero image + icon hosting (Supabase Storage)  |
| ⬜     | API docs & OpenAPI spec                       |
| ⬜     | Deployed REST API (Edge Functions or FastAPI) |

---

## 🔮 Future (Separate Simulator Project)

A separate repository will:

- Use this API to load heroes, skills, gear data
- Implement battle logic, skill triggers, buffs/debuffs
- Simulate rally vs rally, arena, bear trap, etc.
- Validate mechanics using actual battle reports

---

## 📄 License

Community-driven. Not affiliated with Kingshot developers.  
For educational and analytical use only.
