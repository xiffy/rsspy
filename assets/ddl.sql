CREATE TABLE IF NOT EXISTS bookmark (
  ID INTEGER PRIMARY KEY,
  userID INTEGER NOT NULL DEFAULT 0,
  entryID INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
create unique index bookmark on bookmark (entryID, userID);
create INDEX user on bookmark(userID);
create INDEX entry on bookmark (entryID);


CREATE TABLE IF NOT EXISTS entry (
  ID INTEGER PRIMARY KEY,
  feedID INTEGER NOT NULL DEFAULT 0,
  title TEXT,
  description TEXT,
  contents TEXT,
  url TEXT,
  guid TEXT,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  entry_created TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
  published TEXT
);
CREATE INDEX published ON entry (published);
CREATE INDEX feed ON entry (feedID);
CREATE INDEX das_url ON entry (url);
CREATE INDEX das_text ON entry (title, description, contents);

CREATE TABLE IF NOT EXISTS feed (
  ID INTEGER PRIMARY KEY,
  url TEXT,
  title TEXT,
  image TEXT,
  description TEXT,
  update_interval INTEGER DEFAULT 60,
  feed_last_update TIMESTAMP,
  web_url TEXT,
  last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  active INTEGER DEFAULT 1,
  request_options TEXT
);
CREATE INDEX url ON feed (url);

CREATE TABLE IF NOT EXISTS feed_filter (
  ID INTEGER PRIMARY KEY,
  feedID INTEGER DEFAULT 0,
  content_filter TEXT
);

CREATE TABLE IF NOT EXISTS "group" (
  ID INTEGER PRIMARY KEY,
  description TEXT,
  userID INTEGER,
  aggregation TEXT,
  frequency INTEGER,
  last_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  issue INTEGER DEFAULT 1
);
CREATE INDEX FK_group_user ON "group" (userID);
