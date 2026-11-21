# Build an Authentication Anomaly Detector in Python

*Step-by-step tutorial | Python 3.10+ | No third-party packages*

Authentication logs contain clues about account misuse, but unusual activity is not necessarily malicious. This tutorial builds an explainable detector that identifies first-seen source addresses and bursts of failed sign-ins using synthetic data.

## 1. Define the problem

We want to answer two questions for each user:

- Did this user authenticate from a source address not present in the historical baseline?
- Did this user experience at least five failed sign-ins during the current observation window?

The threshold is illustrative, not validated. We preserve individual detection reasons so an analyst can investigate them separately.

## 2. Model the events

Each event has a user, ISO 8601 timestamp, success flag, and source IP.

```python
from datetime import datetime, timedelta, timezone

START = datetime(2026, 1, 5, 9, tzinfo=timezone.utc)

def event(user, hour, success, ip):
    return {
        "user": user,
        "timestamp": (START + timedelta(hours=hour)).isoformat(),
        "success": success,
        "source_ip": ip,
    }
```

The addresses in the example are reserved documentation ranges.

## 3. Construct a historical baseline

```python
from collections import defaultdict

baseline_sources = defaultdict(set)
for row in training:
    baseline_sources[row["user"]].add(row["source_ip"])
```

A set is useful for detecting first-seen sources, but it does not model frequency or account for NAT, corporate proxies, VPN changes, and mobile connections. Production baselines also require safeguards against training on known compromised activity.

## 4. Evaluate the current window

```python
by_user = defaultdict(list)
for row in current:
    by_user[row["user"]].append(row)

for user, rows in sorted(by_user.items()):
    failures = sum(not row["success"] for row in rows)
    sources = {row["source_ip"] for row in rows}
    new_sources = sorted(sources - baseline_sources[user])
```

The set difference returns addresses that were not observed during training. That is a review signal, not proof of intrusion.

## 5. Generate interpretable findings

```python
reasons = []
if failures >= 5:
    reasons.append(f"failure burst ({failures} failures)")
if new_sources:
    reasons.append(f"new source(s): {', '.join(new_sources)}")
```

Keeping reasons explicit makes a rule easier to test, tune, and explain.

## 6. Run the complete detector

The companion [detector.py](detector.py) contains the complete executable example. From the repository root:

```bash
python3 02-python-authentication-anomaly-detection/detector.py
```

Expected output:

```text
alex: REVIEW — failure burst (9 failures); new source(s): 198.51.100.99
sam: no rule triggered
```

## 7. Investigate rather than automatically block

For each finding, validate the IP's relationship to VPN infrastructure, correlate MFA outcomes, inspect subsequent successful logins, and check whether a password reset or help-desk event explains the activity.

Before deploying similar logic, add log deduplication, sliding windows, baseline expiration, missing-data handling, account-type differentiation, and evaluation against labeled historical cases. Measure both missed detections and false positives.

## Conclusion

Simple rules can be useful when they are reproducible and their assumptions are explicit. The goal is to direct analyst attention, not to label every unusual authentication event malicious.

### References

- [Python collections documentation](https://docs.python.org/3/library/collections.html)
- [MITRE ATT&CK T1110: Brute Force](https://attack.mitre.org/techniques/T1110/)

*All data are synthetic. This prototype is educational, not production validated.*