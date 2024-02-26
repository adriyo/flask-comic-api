CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NULL,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255) NOT NULL,  
    status SMALLINT NOT NULL DEFAULT 0,
    role SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS comics (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    image_cover CHARACTER VARYING NULL,
    title CHARACTER VARYING NULL,
    alternative_title CHARACTER VARYING NULL,
    description TEXT NULL,
    status SMALLINT NOT NULL DEFAULT 0,
    type SMALLINT NOT NULL DEFAULT 0,
    published_date DATE NULL,
    user_id SERIAL NOT NULL,
    CONSTRAINT comics_user_id_fkey FOREIGN KEY (user_id) REFERENCES USERS (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NULL
);

CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL 
);

CREATE TABLE IF NOT EXISTS artists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS translators (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS comic_chapters (
    id SERIAL PRIMARY KEY,
    comic_id SERIAL NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    title CHARACTER VARYING NULL,
    CONSTRAINT comic_chapters_comic_id_fkey FOREIGN KEY (comic_id) REFERENCES comics (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chapter_images (
    id SERIAL PRIMARY KEY,
    chapter_id SERIAL NOT NULL,
    image TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT chapter_images_chapter_id_fkey FOREIGN KEY (chapter_id) REFERENCES comic_chapters (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chapter_comments (
    id SERIAL PRIMARY KEY,
    user_id SERIAL NOT NULL,
    chapter_id SERIAL NOT NULL,
    parent_comment_id INT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT chapter_comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT chapter_comments_chapter_id_fkey FOREIGN KEY (chapter_id) REFERENCES comic_chapters (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_bookmarks (
    user_id SERIAL NOT NULL,
    comic_id SERIAL NOT NULL,
    CONSTRAINT user_bookmarks_pk PRIMARY KEY (user_id, comic_id),
    CONSTRAINT user_bookmarks_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT user_bookmarks_comic_id_fkey FOREIGN KEY (comic_id) REFERENCES comics (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comic_authors (
    comic_id SERIAL NOT NULL,
    author_id SERIAL NOT NULL,
    CONSTRAINT comic_authors_pk PRIMARY KEY (comic_id, author_id),
    CONSTRAINT comic_authors_comic_id_fkey FOREIGN KEY (comic_id) REFERENCES comics (id) ON DELETE CASCADE,
    CONSTRAINT comic_authors_author_id_fkey FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comic_artists (
    comic_id SERIAL NOT NULL,
    artist_id SERIAL NOT NULL,
    CONSTRAINT comic_artists_pk PRIMARY KEY (comic_id, artist_id),
    CONSTRAINT comic_artists_comic_id_fkey FOREIGN KEY (comic_id) REFERENCES comics (id) ON DELETE CASCADE,
    CONSTRAINT comic_artists_artist_id_fkey FOREIGN KEY (artist_id) REFERENCES artists (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comic_translators (
    comic_id SERIAL NOT NULL,
    translator_id SERIAL NOT NULL,
    CONSTRAINT comic_translators_pk PRIMARY KEY (comic_id, translator_id),
    CONSTRAINT comic_translators_comic_id_fkey FOREIGN KEY (comic_id) REFERENCES comics (id) ON DELETE CASCADE,
    CONSTRAINT comic_translators_translator_id_fkey FOREIGN KEY (translator_id) REFERENCES translators (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comic_genres (
    comic_id SERIAL NOT NULL,
    genre_id SERIAL NOT NULL,
    CONSTRAINT comic_genres_pk PRIMARY KEY (comic_id, genre_id),
    CONSTRAINT comic_genres_comic_id_fkey FOREIGN KEY (comic_id) REFERENCES comics (id) ON DELETE CASCADE,
    CONSTRAINT comci_genres_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES genres (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comic_tags (
    comic_id SERIAL NOT NULL,
    tag_id SERIAL NOT NULL,
    CONSTRAINT comic_tags_pk PRIMARY KEY (comic_id, tag_id),
    CONSTRAINT comic_tags_comic_id_fkey FOREIGN KEY (comic_id) REFERENCES comics (id) ON DELETE CASCADE,
    CONSTRAINT comci_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
);

COMMENT ON COLUMN comics.type IS '0 - manga, 1 - manhwa, 2 - manhua';
COMMENT ON COLUMN comics.status IS '0 - ongoing, 1 - completed, 2 - hiatus';
COMMENT ON COLUMN users.status IS '0 - waiting confirmation, 1 - confirmed';
COMMENT ON COLUMN users.role IS '0 - creator, 1 - reader, 2 - uploader';