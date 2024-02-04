-- DROP TABLE IF EXISTS chapter_images;
-- DROP TABLE IF EXISTS comic_chapters;
-- DROP TABLE IF EXISTS comics;
-- DROP TABLE IF EXISTS authors;
-- DROP TABLE IF EXISTS users;

create table if not exists users (
    id serial primary key,
    name varchar(100) null,
    email varchar(100) unique,
    password varchar(255) not null,  
    status smallint NOT NULL DEFAULT 0,
    role smallint NOT NULL DEFAULT 0,
    created_at timestamp with time zone not null default now()
);

create table if not exists comics (
    id serial primary key,
    created_at timestamp with time zone not null default now(),
    image_cover_url character varying null,
    title character varying null,
    description text null,
    status smallint not null default '0'::smallint,
    published_date date null,
    author text null,
    user_id serial not null,
    constraint comics_user_id_fkey foreign key (user_id) references users (id) on delete cascade
);

create table if not exists comic_chapters (
    id serial primary key,
    comic_id serial not null,
    created_at timestamp with time zone not null default now(),
    label character varying null,
    constraint comic_chapters_comic_id_fkey foreign key (comic_id) references comics (id) on delete cascade
);

create table if not exists chapter_images (
    id serial primary key,
    chapter_id serial not null,
    url text null,
    created_at timestamp with time zone not null default now(),
    constraint chapter_images_chapter_id_fkey foreign key (chapter_id) references comic_chapters (id) on delete cascade
);

create table if not exists authors (
    id serial primary key,
    name varchar(100) null,
    created_at timestamp with time zone not null default now()
);

COMMENT ON COLUMN users.status IS '0 - waiting confirmation, 1 - confirmed';
COMMENT ON COLUMN users.role IS '0 - creator, 1 - reader';
