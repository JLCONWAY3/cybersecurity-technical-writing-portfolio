# Cybersecurity Technical Writing Portfolio

Original public-facing writing samples covering OT/ICS security, Python detection engineering, and SQL-based authentication analytics.

## Three writing samples

1. [Why Traditional IT Security Monitoring Falls Short in OT Environments](01-ot-security-monitoring/ARTICLE.md) — opinion-driven technical analysis.
2. [Build an Authentication Anomaly Detector in Python](02-python-authentication-anomaly-detection/TUTORIAL.md) — step-by-step tutorial with runnable Python.
3. [Detect Authentication Outliers with SQL](03-sql-statistical-threat-detection/TUTORIAL.md) — statistical detection tutorial with SQLite code.

## Reproduce the examples

Python 3.10+ is sufficient. No third-party packages are required.

```bash
python3 02-python-authentication-anomaly-detection/detector.py
python3 03-sql-statistical-threat-detection/build_data.py
python3 03-sql-statistical-threat-detection/run_query.py
```

All examples use synthetic data and are educational demonstrations rather than production-validated security controls. No proprietary, client, or government operational information is included.
