-- Drop if rerunning during development
drop function if exists slugify(text) cascade;
drop function if exists set_hero_id_slug cascade;

drop type if exists hero_rarity cascade;
drop type if exists hero_class cascade;
drop type if exists skill_type cascade;

-- ENUM: Hero rarity
create type hero_rarity as enum ('Rare', 'Epic', 'Mythic');

-- ENUM: Hero class
create type hero_class as enum ('Infantry', 'Cavalry', 'Archer');

-- ENUM: Skill type (active, passive, special)
create type skill_type as enum ('Active', 'Passive', 'Talent');

-- Helper function to create URL-safe slug from text
create or replace function slugify(text)
    returns text as
$$
select trim(both '-' from regexp_replace(lower(trim($1)), '[^a-z0-9]+', '-', 'g'));
$$ language sql immutable;

-- Trigger function to automatically create hero_id_slug on insert
create or replace function set_hero_id_slug()
    returns trigger as
$$
begin
    if new.hero_id_slug is null or new.hero_id_slug = '' then
        new.hero_id_slug := slugify(new.name);
    end if;
    return new;
end;
$$ language plpgsql;
