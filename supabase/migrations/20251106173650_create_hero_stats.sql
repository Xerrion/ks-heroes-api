drop table if exists hero_conquest_stats cascade;

create table hero_conquest_stats
(
    id         uuid primary key default gen_random_uuid(),
    hero_id    uuid not null unique references heroes (id) on delete cascade,
    attack     int  not null check (attack >= 0),
    defense    int  not null check (defense >= 0),
    health     int  not null check (health >= 0),
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);