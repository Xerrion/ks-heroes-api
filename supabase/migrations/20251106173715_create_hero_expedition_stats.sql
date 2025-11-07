drop table if exists hero_expedition_stats cascade;

create table hero_expedition_stats
(
    id          uuid primary key default gen_random_uuid(),
    hero_id     uuid       not null unique references heroes (id) on delete cascade,
    troop_type  hero_class not null,
    attack_pct  numeric(8, 2) not null check (attack_pct >= 0),
    defense_pct numeric(8, 2) not null check (defense_pct >= 0),
    created_at  timestamptz default now(),
    updated_at  timestamptz default now()
);