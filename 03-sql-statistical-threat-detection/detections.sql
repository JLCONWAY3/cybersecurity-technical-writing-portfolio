WITH daily AS (
  SELECT user_id, day,
    SUM(CASE WHEN outcome = 'failure' THEN 1 ELSE 0 END) AS failures
  FROM auth_events GROUP BY user_id, day
), baseline AS (
  SELECT user_id,
    AVG(1.0 * failures) AS mean_failures,
    MAX(0.0, AVG(1.0 * failures * failures)
      - AVG(1.0 * failures) * AVG(1.0 * failures)) AS variance
  FROM daily WHERE day < '2026-01-08' GROUP BY user_id
), scored AS (
  SELECT d.user_id, d.failures, b.mean_failures,
    CASE WHEN b.variance > 0
      THEN (d.failures - b.mean_failures) / SQRT(b.variance)
      ELSE NULL END AS z_score,
    CASE WHEN b.variance = 0 AND d.failures > b.mean_failures
      THEN 1 ELSE 0 END AS zero_variance_jump
  FROM daily d JOIN baseline b USING (user_id)
  WHERE d.day = '2026-01-08'
)
SELECT user_id, failures, mean_failures, z_score, zero_variance_jump
FROM scored WHERE zero_variance_jump = 1 OR z_score >= 3
ORDER BY user_id;
