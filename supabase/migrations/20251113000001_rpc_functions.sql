-- RPC Functions for efficient hero data retrieval
-- Optimized for battle simulator consumption
-- Created: 2025-11-13

BEGIN;

-- =============================================================================
-- GET COMPLETE HERO DATA
-- =============================================================================

CREATE OR REPLACE FUNCTION get_hero_complete(hero_slug TEXT)
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'hero', (
      SELECT json_build_object(
        'id', h.id,
        'hero_id_slug', h.hero_id_slug,
        'name', h.name,
        'rarity', h.rarity,
        'generation', h.generation,
        'class', h.class,
        'image_path', h.image_path,
        'sources', h.sources
      )
      FROM heroes h
      WHERE h.hero_id_slug = hero_slug
    ),
    'conquest_stats', (
      SELECT json_build_object(
        'attack', cs.attack,
        'defense', cs.defense,
        'health', cs.health
      )
      FROM hero_conquest_stats cs
      JOIN heroes h ON h.id = cs.hero_id
      WHERE h.hero_id_slug = hero_slug
    ),
    'expedition_stats', (
      SELECT json_build_object(
        'troop_type', es.troop_type,
        'attack_pct', es.attack_pct,
        'defense_pct', es.defense_pct,
        'lethality_pct', es.lethality_pct,
        'health_pct', es.health_pct
      )
      FROM hero_expedition_stats es
      JOIN heroes h ON h.id = es.hero_id
      WHERE h.hero_id_slug = hero_slug
    ),
    'conquest_skills', (
      SELECT COALESCE(json_agg(
        json_build_object(
          'id', s.id,
          'name', s.name,
          'type', s.skill_type,
          'description', s.description,
          'icon_path', s.icon_path,
          'effect_category', s.effect_category,
          'effect_op', s.effect_op,
          'levels', (
            SELECT json_object_agg(
              sl.level::text,
              sl.effects
            )
            FROM hero_skill_levels sl
            WHERE sl.skill_id = s.id
            ORDER BY sl.level
          )
        )
        ORDER BY s.skill_type, s.name
      ), '[]'::json)
      FROM hero_skills s
      JOIN heroes h ON h.id = s.hero_id
      WHERE h.hero_id_slug = hero_slug
        AND s.battle_type = 'Conquest'
    ),
    'expedition_skills', (
      SELECT COALESCE(json_agg(
        json_build_object(
          'id', s.id,
          'name', s.name,
          'type', s.skill_type,
          'description', s.description,
          'icon_path', s.icon_path,
          'effect_category', s.effect_category,
          'effect_op', s.effect_op,
          'levels', (
            SELECT json_object_agg(
              sl.level::text,
              sl.effects
            )
            FROM hero_skill_levels sl
            WHERE sl.skill_id = s.id
            ORDER BY sl.level
          )
        )
        ORDER BY s.skill_type, s.name
      ), '[]'::json)
      FROM hero_skills s
      JOIN heroes h ON h.id = s.hero_id
      WHERE h.hero_id_slug = hero_slug
        AND s.battle_type = 'Expedition'
    ),
    'talent', (
      SELECT json_build_object(
        'id', t.id,
        'name', t.name,
        'description', t.description,
        'icon_path', t.icon_path,
        'max_level_effects', t.max_level_effects
      )
      FROM hero_talents t
      JOIN heroes h ON h.id = t.hero_id
      WHERE h.hero_id_slug = hero_slug
    ),
    'exclusive_gear', (
      SELECT json_build_object(
        'id', g.id,
        'name', g.name,
        'image_path', g.image_path,
        'levels', (
          SELECT json_object_agg(
            gl.level::text,
            json_build_object(
              'power', gl.power,
              'hero_attack', gl.hero_attack,
              'hero_defense', gl.hero_defense,
              'hero_health', gl.hero_health,
              'troop_lethality_bonus', gl.troop_lethality_bonus,
              'troop_health_bonus', gl.troop_health_bonus,
              'conquest_skill_effect', gl.conquest_skill_effect,
              'expedition_skill_effect', gl.expedition_skill_effect
            )
          )
          FROM hero_exclusive_gear_levels gl
          WHERE gl.gear_id = g.id
          ORDER BY gl.level
        ),
        'conquest_skill', (
          SELECT json_build_object(
            'id', gs.id,
            'name', gs.name,
            'description', gs.description,
            'max_effect', gs.max_effect,
            'progression', (
              SELECT json_object_agg(
                gsl.gear_level::text,
                json_build_object(
                  'tier', gsl.skill_tier,
                  'value', gsl.upgrade_value
                )
              )
              FROM hero_exclusive_gear_skill_levels gsl
              WHERE gsl.skill_id = gs.id
              ORDER BY gsl.gear_level
            )
          )
          FROM hero_exclusive_gear_skills gs
          WHERE gs.gear_id = g.id AND gs.battle_type = 'Conquest'
        ),
        'expedition_skill', (
          SELECT json_build_object(
            'id', gs.id,
            'name', gs.name,
            'description', gs.description,
            'max_effect', gs.max_effect,
            'progression', (
              SELECT json_object_agg(
                gsl.gear_level::text,
                json_build_object(
                  'tier', gsl.skill_tier,
                  'value', gsl.upgrade_value
                )
              )
              FROM hero_exclusive_gear_skill_levels gsl
              WHERE gsl.skill_id = gs.id
              ORDER BY gsl.gear_level
            )
          )
          FROM hero_exclusive_gear_skills gs
          WHERE gs.gear_id = g.id AND gs.battle_type = 'Expedition'
        )
      )
      FROM hero_exclusive_gear g
      JOIN heroes h ON h.id = g.hero_id
      WHERE h.hero_id_slug = hero_slug
    )
  ) INTO result;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_hero_complete(TEXT) IS 'Get complete hero data including all stats, skills, talents, and gear';

-- =============================================================================
-- GET ALL EXPEDITION HEROES (optimized for battle simulator)
-- =============================================================================

CREATE OR REPLACE FUNCTION get_all_expedition_heroes()
RETURNS JSON AS $$
BEGIN
  RETURN (
    SELECT json_agg(
      json_build_object(
        'hero_id_slug', h.hero_id_slug,
        'name', h.name,
        'rarity', h.rarity,
        'generation', h.generation,
        'class', h.class,
        'image_path', h.image_path,
        'expedition_stats', json_build_object(
          'troop_type', es.troop_type,
          'attack_pct', es.attack_pct,
          'defense_pct', es.defense_pct,
          'lethality_pct', es.lethality_pct,
          'health_pct', es.health_pct
        ),
        'expedition_skills', (
          SELECT COALESCE(json_agg(
            json_build_object(
              'name', s.name,
              'type', s.skill_type,
              'description', s.description,
              'effect_category', s.effect_category,
              'effect_op', s.effect_op,
              'levels', (
                SELECT json_object_agg(sl.level::text, sl.effects)
                FROM hero_skill_levels sl
                WHERE sl.skill_id = s.id
                ORDER BY sl.level
              )
            )
            ORDER BY s.skill_type, s.name
          ), '[]'::json)
          FROM hero_skills s
          WHERE s.hero_id = h.id AND s.battle_type = 'Expedition'
        ),
        'exclusive_gear', (
          SELECT json_build_object(
            'name', g.name,
            'expedition_skill', (
              SELECT json_build_object(
                'name', gs.name,
                'description', gs.description,
                'progression', (
                  SELECT json_object_agg(
                    gsl.gear_level::text,
                    json_build_object('tier', gsl.skill_tier, 'value', gsl.upgrade_value)
                  )
                  FROM hero_exclusive_gear_skill_levels gsl
                  WHERE gsl.skill_id = gs.id
                )
              )
              FROM hero_exclusive_gear_skills gs
              WHERE gs.gear_id = g.id AND gs.battle_type = 'Expedition'
            ),
            'levels', (
              SELECT json_object_agg(
                gl.level::text,
                json_build_object(
                  'power', gl.power,
                  'hero_attack', gl.hero_attack,
                  'hero_defense', gl.hero_defense,
                  'hero_health', gl.hero_health,
                  'troop_lethality_bonus', gl.troop_lethality_bonus,
                  'troop_health_bonus', gl.troop_health_bonus,
                  'expedition_skill_effect', gl.expedition_skill_effect
                )
              )
              FROM hero_exclusive_gear_levels gl
              WHERE gl.gear_id = g.id
            )
          )
          FROM hero_exclusive_gear g
          WHERE g.hero_id = h.id
        )
      )
      ORDER BY h.rarity DESC, h.generation DESC, h.name
    )
    FROM heroes h
    LEFT JOIN hero_expedition_stats es ON es.hero_id = h.id
  );
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_all_expedition_heroes() IS 'Get all heroes with expedition-relevant data for battle simulator';

-- =============================================================================
-- GET HEROES BY CLASS (for joiner selection)
-- =============================================================================

CREATE OR REPLACE FUNCTION get_heroes_by_class(hero_class_filter hero_class)
RETURNS JSON AS $$
BEGIN
  RETURN (
    SELECT json_agg(
      json_build_object(
        'hero_id_slug', h.hero_id_slug,
        'name', h.name,
        'rarity', h.rarity,
        'generation', h.generation,
        'class', h.class,
        'image_path', h.image_path
      )
      ORDER BY h.rarity DESC, h.generation DESC, h.name
    )
    FROM heroes h
    WHERE h.class = hero_class_filter
  );
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_heroes_by_class(hero_class) IS 'Get heroes filtered by class (Infantry, Cavalry, Archer)';

-- =============================================================================
-- SEARCH HEROES
-- =============================================================================

CREATE OR REPLACE FUNCTION search_heroes(search_query TEXT)
RETURNS JSON AS $$
BEGIN
  RETURN (
    SELECT json_agg(
      json_build_object(
        'hero_id_slug', h.hero_id_slug,
        'name', h.name,
        'rarity', h.rarity,
        'generation', h.generation,
        'class', h.class,
        'image_path', h.image_path
      )
      ORDER BY 
        similarity(h.name, search_query) DESC,
        h.rarity DESC,
        h.generation DESC
    )
    FROM heroes h
    WHERE h.name ILIKE '%' || search_query || '%'
       OR h.hero_id_slug ILIKE '%' || search_query || '%'
    LIMIT 50
  );
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION search_heroes(TEXT) IS 'Search heroes by name or slug';

COMMIT;
