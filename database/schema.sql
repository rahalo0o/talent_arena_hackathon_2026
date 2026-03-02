-- Talent Arena Hackathon 2026 Database Schema

PRAGMA foreign_keys = ON;

-- Users: participants, judges, and organizers
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,
    email       TEXT    NOT NULL UNIQUE,
    full_name   TEXT    NOT NULL,
    role        TEXT    NOT NULL CHECK(role IN ('participant', 'judge', 'organizer')),
    bio         TEXT,
    avatar_url  TEXT,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Categories/Tracks for the hackathon
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    description TEXT,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Teams
CREATE TABLE IF NOT EXISTS teams (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    description TEXT,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Team memberships (many users ↔ many teams)
CREATE TABLE IF NOT EXISTS team_members (
    team_id     INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_leader   INTEGER NOT NULL DEFAULT 0 CHECK(is_leader IN (0, 1)),
    joined_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (team_id, user_id)
);

-- Projects submitted by teams
CREATE TABLE IF NOT EXISTS projects (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id      INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    category_id  INTEGER NOT NULL REFERENCES categories(id),
    title        TEXT    NOT NULL,
    description  TEXT,
    repo_url     TEXT,
    demo_url     TEXT,
    status       TEXT    NOT NULL DEFAULT 'draft'
                         CHECK(status IN ('draft', 'submitted', 'under_review', 'finalist', 'winner')),
    submitted_at DATETIME,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Scores given by judges to projects
CREATE TABLE IF NOT EXISTS scores (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id   INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    judge_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    innovation   INTEGER NOT NULL CHECK(innovation  BETWEEN 1 AND 10),
    impact       INTEGER NOT NULL CHECK(impact      BETWEEN 1 AND 10),
    technical    INTEGER NOT NULL CHECK(technical   BETWEEN 1 AND 10),
    presentation INTEGER NOT NULL CHECK(presentation BETWEEN 1 AND 10),
    comment      TEXT,
    scored_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (project_id, judge_id)
);

-- Events / schedule items
CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    description TEXT,
    location    TEXT,
    starts_at   DATETIME NOT NULL,
    ends_at     DATETIME NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Announcements
CREATE TABLE IF NOT EXISTS announcements (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id    INTEGER NOT NULL REFERENCES users(id),
    title        TEXT    NOT NULL,
    body         TEXT    NOT NULL,
    published_at DATETIME,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
