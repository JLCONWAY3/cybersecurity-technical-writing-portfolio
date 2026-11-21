from collections import defaultdict
from datetime import datetime, timedelta, timezone

START = datetime(2026, 1, 5, 9, tzinfo=timezone.utc)

def event(user, hour, success, ip):
    return {"user": user, "timestamp": (START + timedelta(hours=hour)).isoformat(),
            "success": success, "source_ip": ip}

training = [
    event("alex", -24, True, "192.0.2.10"),
    event("alex", -12, True, "192.0.2.10"),
    event("sam", -24, True, "192.0.2.20"),
]
current = [event("alex", i, False, "198.51.100.99") for i in range(9)]
current += [event("sam", 1, True, "192.0.2.20")]

baseline_sources = defaultdict(set)
for row in training:
    baseline_sources[row["user"]].add(row["source_ip"])

by_user = defaultdict(list)
for row in current:
    by_user[row["user"]].append(row)

for user, rows in sorted(by_user.items()):
    failures = sum(not row["success"] for row in rows)
    new_sources = sorted({row["source_ip"] for row in rows} - baseline_sources[user])
    reasons = []
    if failures >= 5:
        reasons.append(f"failure burst ({failures} failures)")
    if new_sources:
        reasons.append(f"new source(s): {', '.join(new_sources)}")
    print(f"{user}: " + ("REVIEW — " + "; ".join(reasons) if reasons else "no rule triggered"))
