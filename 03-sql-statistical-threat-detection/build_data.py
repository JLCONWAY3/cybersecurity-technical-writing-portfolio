import sqlite3
from pathlib import Path

db = Path(__file__).with_name("auth_events.db")
with sqlite3.connect(db) as con:
    con.execute("DROP TABLE IF EXISTS auth_events")
    con.execute("CREATE TABLE auth_events (user_id TEXT, day TEXT, source_ip TEXT, outcome TEXT)")
    for day in range(1, 9):
        date = f"2026-01-{day:02d}"
        for user, count in (("alex", 12 if day == 8 else 1), ("sam", 2), ("lee", 0)):
            for i in range(max(count, 1)):
                outcome = "failure" if i < count else "success"
                con.execute("INSERT INTO auth_events VALUES (?, ?, ?, ?)",
                            (user, date, "192.0.2.10", outcome))
print(f"Created {db}")
