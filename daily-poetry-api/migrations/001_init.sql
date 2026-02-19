CREATE TABLE IF NOT EXISTS authors (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  bio_short TEXT,
  image_url TEXT
);

CREATE TABLE IF NOT EXISTS poems (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  text TEXT NOT NULL,
  linecount INTEGER NOT NULL,
  author_id TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES authors(id)
);

CREATE TABLE IF NOT EXISTS daily_selection (
  date TEXT PRIMARY KEY,
  poem_id TEXT NOT NULL,
  FOREIGN KEY (poem_id) REFERENCES poems(id)
);

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  auth_token TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS favourites (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  poem_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (poem_id) REFERENCES poems(id),
  CONSTRAINT uq_favourites_user_poem UNIQUE (user_id, poem_id)
);

CREATE INDEX IF NOT EXISTS idx_poems_author_id ON poems(author_id);
CREATE INDEX IF NOT EXISTS idx_daily_selection_poem_id ON daily_selection(poem_id);
CREATE INDEX IF NOT EXISTS idx_favourites_user_id ON favourites(user_id);
CREATE INDEX IF NOT EXISTS idx_favourites_poem_id ON favourites(poem_id);
