-- Week 8 SQL queries, run against the clean dataset in data/processed/posts_clean.csv
-- The `posts` table is loaded from the CSV by scripts/run_sql.py (SQLite).
-- Use: python3 scripts/run_sql.py

-- Total volume by intent category
SELECT category, COUNT(*) AS posts
FROM posts
GROUP BY category
ORDER BY posts DESC;

-- Peak loneliness hours: volume by hour of day (Asia/Manila)
SELECT hour_manila, COUNT(*) AS posts
FROM posts
GROUP BY hour_manila
ORDER BY posts DESC
LIMIT 10;

-- Volume by day of week
SELECT day_of_week, COUNT(*) AS posts
FROM posts
GROUP BY day_of_week
ORDER BY posts DESC;

-- Cities ranked by volume with intent mix (city extracted in transform.py via
-- gazetteer-based geoparsing, canonical names from the PSGC publication)
SELECT city, COUNT(*) AS posts,
       ROUND(100.0 * SUM(CASE WHEN category = 'platonic' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_platonic,
       ROUND(100.0 * SUM(CASE WHEN category = 'romantic' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_romantic,
       ROUND(100.0 * SUM(CASE WHEN category = 'sexual' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_sexual
FROM posts
WHERE city != ''
GROUP BY city
ORDER BY posts DESC
LIMIT 15;

-- Intent mix by hour, to see if platonic and sexual peaks differ
SELECT hour_manila,
       SUM(CASE WHEN category = 'platonic' THEN 1 ELSE 0 END) AS platonic,
       SUM(CASE WHEN category = 'romantic' THEN 1 ELSE 0 END) AS romantic,
       SUM(CASE WHEN category = 'sexual' THEN 1 ELSE 0 END) AS sexual
FROM posts
GROUP BY hour_manila
ORDER BY hour_manila;

-- Seeker gender split by intent category
SELECT category, seeker_gender, COUNT(*) AS posts
FROM posts
WHERE seeker_gender IS NOT NULL
GROUP BY category, seeker_gender
ORDER BY category, posts DESC;

-- Monthly trend
SELECT year, month, COUNT(*) AS posts
FROM posts
GROUP BY year, month
ORDER BY year, month;

-- Age profile of connection seekers
SELECT category,
       COUNT(seeker_age) AS with_age,
       ROUND(AVG(seeker_age), 1) AS avg_age,
       MIN(seeker_age) AS min_age,
       MAX(seeker_age) AS max_age
FROM posts
GROUP BY category
ORDER BY category;
