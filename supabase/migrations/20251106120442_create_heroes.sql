-- Drop if re-running during development
drop table if exists heroes cascade;

create table heroes
(
    id           uuid primary key default gen_random_uuid(),
    hero_id_slug text        not null unique,
    name         text        not null,
    rarity       hero_rarity not null,
    generation   int,
    class        hero_class  not null,
    image_path   text,
    created_at   timestamptz      default now(),
    updated_at   timestamptz      default now()
);

-- Trigger: Automatically create slug from hero name
create trigger trigger_set_hero_id_slug
    before insert
    on heroes
    for each row
execute function set_hero_id_slug();