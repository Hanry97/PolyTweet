DROP TABLE IF EXISTS tweets;
DROP TABLE IF EXISTS candidats;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS youtube;

CREATE TABLE candidats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    parti_poli TEXT NOT NULL,
    twitter_username TEXT NOT NULL,
    count_tweets TEXT NOT NULL,
    count_following TEXT NOT NULL,
    count_followers TEXT NOT NULL,
    count_likes TEXT NOT NULL,
    url_photo TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tweets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT NOT NULL,
    tweet TEXT NOT NULL,
    username TEXT NOT NULL,
    candidat_id INTEGER,
    score REAL DEFAULT -100,
    score_vader REAL DEFAULT -100,
    score_textblob REAL DEFAULT -100,
    long REAL DEFAULT 0.0,
    lat REAL DEFAULT 0.0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(candidat_id) REFERENCES candidats(id)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE youtube (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score REAL,
    avis_pos REAL,
    avis_neg REAL,
    nb_comments INTEGER,
    candidat_id INTEGER,
    emission TEXT NOT NULL,
    date_emission TEXT NOT NULL,
    id_video TEXT NOT NULL,
    FOREIGN KEY(candidat_id) REFERENCES candidats(id)
);
