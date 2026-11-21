import sqlite3
from pathlib import Path

folder = Path(__file__).resolve().parent
with sqlite3.connect(folder / "auth_events.db") as con:
    sql = (folder / "detections.sql").read_text(encoding="utf-8")
    for row in con.execute(sql):
        print("|".join("" if value is None else str(value) for value in row))
