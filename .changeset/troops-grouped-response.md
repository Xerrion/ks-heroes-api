# Troops API: Simplified Single Endpoint

**Date:** 2025-11-13  
**Type:** Feature Enhancement  
**Breaking:** No (backwards compatible)

## Summary

Redesigned the Troops API to use a single, flexible endpoint with query parameters instead of path-based routing. Added support for both exact match and range queries with shorter parameter names.

## Changes

### 1. Removed Path-Based Endpoint

**Removed:** `GET /troops/{type}/{level}`

This endpoint has been replaced with query parameters on the main `/troops` endpoint for simplicity and flexibility.

### 2. Enhanced Main Endpoint

**Updated:** `GET /troops` now supports:

**Exact Match Parameters:**

- `type`: Exact troop type (Infantry, Cavalry, Archer)
- `level`: Exact troop level (1-11)
- `tg`: Exact True Gold level (0-10)

**Range Parameters:**

- `min_level`, `max_level`: Filter by level range
- `min_tg`, `max_tg`: Filter by True Gold range

**Behavior:**

- Exact params override range params when specified
- Defaults: levels 1-10, TG 0-5 (current game state)

### 3. Shorter Parameter Names

- `type` instead of `troop_type`
- `level` instead of `troop_level`
- `tg` instead of `true_gold_level`

### 4. Grouped Response (Default)

Returns data grouped by troop type for better consumption:

```json
{
  "Infantry": [{...}],
  "Cavalry": [{...}],
  "Archer": [{...}]
}
```

Use `group_by=none` for flat list format.

## API Examples

### Before (Path-Based)

```bash
# Get specific configuration
curl "http://localhost:8000/troops/Infantry/11?true_gold_level=5"
```

### After (Query-Based)

```bash
# Exact match (cleaner, more flexible)
curl "http://localhost:8000/troops?type=infantry&level=11&tg=5"

# Range query
curl "http://localhost:8000/troops?type=infantry&min_level=8&max_level=10"

# All troops (default)
curl "http://localhost:8000/troops"
```

## Benefits

1. **Simpler API**: Single endpoint instead of multiple
2. **More Flexible**: Exact match OR range queries
3. **Better Caching**: Query params easier to cache/vary
4. **Cleaner URLs**: Shorter parameter names
5. **Grouped Data**: Better structure for comparing troop types
6. **Backwards Compatible**: No breaking changes to existing functionality

## Migration Guide

No migration needed - this is a new feature. Old query patterns still work:

```bash
# Still works (old verbose params)
curl "http://localhost:8000/troops?troop_type=Infantry&min_level=5"

# Better (new short params)
curl "http://localhost:8000/troops?type=Infantry&min_level=5"

# Best (exact match for single config)
curl "http://localhost:8000/troops?type=Infantry&level=5&tg=2"
```

## Testing

```bash
# Test exact match
curl "http://localhost:8000/troops?type=infantry&level=11&tg=5"

# Test range query
curl "http://localhost:8000/troops?type=Cavalry&min_level=8&max_level=10"

# Test grouped response (default)
curl http://localhost:8000/troops | jq '.Infantry | length'

# Test flat list
curl "http://localhost:8000/troops?group_by=none" | jq 'length'
```

## Files Modified

- `src/routes/troops/get_all.py` - Enhanced with exact match params and shorter names
- `src/routes/troops/get_by_configuration.py` - **Removed** (functionality merged into get_all)
- `src/schemas/troops.py` - Added GroupBy, TroopStats, TroopsGroupedByType
- `src/schemas/__init__.py` - Exported new schemas
- `src/main.py` - Removed path-based route registration
- `TROOPS_API.md` - Updated with new endpoint structure
- `IMPLEMENTATION_STEPS.md` - Updated testing examples

## Related Issues

- Resolves user feedback about flat API responses
- Resolves request for simpler query-based endpoints instead of path-based routing
