# talent_arena_hackathon_2026

A platform for the Talent Arena Hackathon 2026.

## Database

The project uses **SQLite** (via Python's built-in `sqlite3` module). No external dependencies are required.

### Schema

| Table           | Description                                        |
|-----------------|----------------------------------------------------|
| `users`         | Participants, judges, and organizers               |
| `categories`    | Hackathon tracks (e.g. AI, Web, Sustainability)    |
| `teams`         | Competing teams                                    |
| `team_members`  | Many-to-many mapping of users ↔ teams              |
| `projects`      | Submissions linked to a team and category          |
| `scores`        | Judge scores for each project (1–10 per criterion) |
| `events`        | Schedule items / sessions                          |
| `announcements` | Organizer announcements                            |

### Setup

```bash
# Create the schema only
python database/setup.py

# Create the schema and insert sample data
python database/setup.py --seed
```

The database file is written to `database/talent_arena.db` (excluded from version control via `.gitignore`).
