-- 010_create_rpc_api_get_hero.sql

create or replace function api_get_hero(hero_slug text)
returns json
language sql
stable
as $$
  select json_build_object(
    'hero_id', h.id,
    'slug', h.hero_id_slug,
    'name', h.name,
    'class', h.class,
    'rarity', h.rarity,
    'generation', h.generation,
    'expedition_stats', case
        when hes.hero_id is null then null
        else json_build_object(
          'troop_type', hes.troop_type,
          'attack_pct', hes.attack_pct,
          'defense_pct', hes.defense_pct
        )
    end,
    'conquest_stats', case
        when hs.hero_id is null then null
        else json_build_object(
          'attack', hs.attack,
          'defense', hs.defense,
          'health', hs.health
        )
    end,
    'skills', (
      select json_agg(
        json_build_object(
          'name', s.name,
          'type', s.skill_type,
          'battle_type', s.battle_type,
          'description', s.description,
          'levels', (
            select json_agg(
              json_build_object(
                'level', sl.level,
                'effects', sl.effects
              )
              order by sl.level
                   )
            from hero_skill_levels sl
            where sl.skill_id = s.id
          )
        )
        order by s.battle_type, s.name
      )
      from hero_skills s
      where s.hero_id = h.id
    ),
    'exclusive_gear', (
      select json_build_object(
        'name', g.name,
        'levels', (
          select json_agg(
            json_build_object(
              'level', gl.level,
              'power', gl.power,
              'hero_attack', gl.hero_attack,
              'hero_defense', gl.hero_defense,
              'hero_health', gl.hero_health,
              'troop_lethality', gl.troop_lethality,
              'troop_health', gl.troop_health
            )
            order by gl.level
                 )
          from hero_exclusive_gear_levels gl
          where gl.gear_id = g.id
        ),
        'skills', (
          select json_agg(
            json_build_object(
              'skill_type', gs.skill_type,
              'name', gs.name,
              'description', gs.description,
              'effects', gs.effects
            )
          )
          from hero_exclusive_gear_skills gs
          where gs.gear_id = g.id
        )
      )
      from hero_exclusive_gear g
      where g.hero_id = h.id
    )
  )
  from heroes h
  left join hero_conquest_stats hs on hs.hero_id = h.id
  left join hero_expedition_stats hes on hes.hero_id = h.id
  where h.hero_id_slug = hero_slug;
$$;