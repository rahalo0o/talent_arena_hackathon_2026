"""
Setup script: creates the SQLite database and optionally seeds it with sample data.

Usage:
    python database/setup.py           # create schema only
    python database/setup.py --seed    # create schema + insert sample data
"""

import argparse
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "talent_arena.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def create_schema(conn: sqlite3.Connection) -> None:
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    print("Schema applied.")


def seed_data(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    # Sample categories
    categories = [
        ("AI & Machine Learning", "Projects leveraging artificial intelligence or ML models."),
        ("Web & Mobile", "Web applications and mobile apps."),
        ("Sustainability", "Solutions targeting environmental or social sustainability."),
        ("Developer Tools", "Tools and frameworks improving developer productivity."),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
        categories,
    )

    # Sample users
    users = [
        ("alice", "alice@example.com", "Alice Smith", "organizer", "Event organizer."),
        ("bob",   "bob@example.com",   "Bob Jones",  "judge",     "Industry expert."),
        ("carol", "carol@example.com", "Carol White", "participant", "Full-stack dev."),
        ("dave",  "dave@example.com",  "Dave Brown",  "participant", "ML engineer."),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO users (username, email, full_name, role, bio) VALUES (?, ?, ?, ?, ?)",
        users,
    )

    # Sample team
    cursor.execute("INSERT OR IGNORE INTO teams (name, description) VALUES (?, ?)",
                   ("Team Alpha", "Building the future with AI."))
    team_id = cursor.execute("SELECT id FROM teams WHERE name = 'Team Alpha'").fetchone()[0]

    for username in ("carol", "dave"):
        user_id = cursor.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()[0]
        cursor.execute(
            "INSERT OR IGNORE INTO team_members (team_id, user_id, is_leader) VALUES (?, ?, ?)",
            (team_id, user_id, 1 if username == "carol" else 0),
        )

    # Sample project
    category_id = cursor.execute(
        "SELECT id FROM categories WHERE name = 'AI & Machine Learning'"
    ).fetchone()[0]
    cursor.execute(
        """INSERT OR IGNORE INTO projects
           (team_id, category_id, title, description, repo_url, status, submitted_at)
           VALUES (?, ?, ?, ?, ?, 'submitted', CURRENT_TIMESTAMP)""",
        (
            team_id,
            category_id,
            "SmartTalent Matcher",
            "An AI-powered platform that matches talents with opportunities.",
            "https://github.com/example/smart-talent-matcher",
        ),
    )

    # Sample event
    cursor.execute(
        """INSERT OR IGNORE INTO events (title, description, location, starts_at, ends_at)
           VALUES (?, ?, ?, ?, ?)""",
        (
            "Hackathon Kick-off",
            "Opening ceremony and rules explanation.",
            "Main Hall",
            "2026-03-15 09:00:00",
            "2026-03-15 10:00:00",
        ),
    )

    conn.commit()
    print("Sample data inserted.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up the Talent Arena database.")
    parser.add_argument("--seed", action="store_true", help="Insert sample data after creating schema.")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    try:
        create_schema(conn)
        if args.seed:
            seed_data(conn)
        print(f"Database ready at: {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
