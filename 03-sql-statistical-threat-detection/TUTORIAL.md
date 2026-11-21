# Detect Authentication Outliers with SQL: Baselines and Z-Scores

*Step-by-step tutorial | SQLite and Python 3.10+*

A global threshold for failed logins is easy to implement but ignores differences among users. A per-user baseline can reveal sudden changes, provided we handle statistical edge cases honestly.

This tutorial generates synthetic daily authentication counts, computes a seven-day baseline, and flags unexpected increases.

## 1. Prepare the dataset

Run the data generator:

```bash
python3 03-sql-statistical-threat-detection/build_data.py
```

It creates `auth_events.db` containing `user_id`, `day`, `source_ip`, and `outcome`. During January 1–7, alex has one failure daily, sam has two, and lee has none. On January 8, alex has twelve failures.

## 2. Aggregate daily failures

```sql
WITH daily AS (
  SELECT user_id, day,
         SUM(CASE WHEN outcome = 'failure' THEN 1 ELSE 0 END) AS failures
  FROM auth_events
  GROUP BY user_id, day
)
SELECT * FROM daily;
```

In production, daily aggregation should also account for missing event coverage, retries, and inconsistent provider-specific failure semantics.

## 3. Calculate the baseline

For each user, estimate mean failures and population variance over the preceding seven days:

```text
variance = E[X²] - (E[X])²
```

```sql
baseline AS (
  SELECT user_id,
         AVG(1.0 * failures) AS mean_failures,
         AVG(1.0 * failures * failures)
           - AVG(1.0 * failures) * AVG(1.0 * failures) AS variance
  FROM daily
  WHERE day < '2026-01-08'
  GROUP BY user_id
)
```

The formula is simple but can suffer floating-point cancellation with very large values.

## 4. Avoid dividing by zero

A z-score is `(observed - mean) / standard_deviation`. If the historical standard deviation is zero, that quantity is undefined.

Instead, report a separate Boolean flag when the observed value exceeds a constant baseline:

```sql
CASE WHEN b.variance > 0
     THEN (d.failures - b.mean_failures) / SQRT(b.variance)
     ELSE NULL END AS z_score,
CASE WHEN b.variance = 0 AND d.failures > b.mean_failures
     THEN 1 ELSE 0 END AS zero_variance_jump
```

The flag is not a statistical significance test. A seven-day sample is too small to justify strong distributional claims.

## 5. Execute the complete query

The complete [detections.sql](detections.sql) query is included. Run the Python wrapper to avoid requiring a separate SQLite command-line installation:

```bash
python3 03-sql-statistical-threat-detection/run_query.py
```

Expected result:

```text
alex|12|1.0||1
```

The empty fourth field is a NULL z-score. The final field is the zero-variance jump flag.

## 6. Interpret the finding

Alex had twelve failures compared with one per day historically. This is a reason to investigate, not evidence that an attacker was responsible.

Correlate the result with source IP changes, MFA outcomes, subsequent successful logins, and legitimate password-reset or help-desk activity.

**Missing-day caveat:** if no event is recorded on a day, the query may omit that date rather than count zero failures. Production pipelines should build a complete identity-by-date calendar and fill zeros only after confirming telemetry completeness.

## 7. Improve the design

Possible extensions include rolling 30-day baselines, peer-group comparison, robust median/MAD methods, service-account segmentation, and source-level aggregation. Each extension should be evaluated for false positives and operational utility.

### References

- [SQLite aggregate functions](https://www.sqlite.org/lang_aggfunc.html)
- [SQLite math functions](https://www.sqlite.org/lang_mathfunc.html)
- [MITRE ATT&CK T1110](https://attack.mitre.org/techniques/T1110/)

*All data are synthetic. The detection is an educational example, not a production-validated rule.*