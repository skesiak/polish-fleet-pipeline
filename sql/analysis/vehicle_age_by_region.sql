SELECT
    v.voivodeship_name,
    COUNT(*) AS registrations,
    ROUND(AVG(age_at_registration), 1) AS avg_age,
    MEDIAN(age_at_registration) as median_age,
    ROUND(COUNT(*) FILTER (WHERE age_at_registration >= 10) * 100.0 / COUNT(*), 1) AS pct_aged_10_plus,
    ROUND(COUNT(*) FILTER (WHERE origin_category = 'used_import') * 100.0 / COUNT(*), 1) AS pct_used_import,
    ROW_NUMBER() OVER (ORDER BY MEDIAN(age_at_registration) DESC) AS age_rank
FROM stg_vehicles s
JOIN read_csv_auto('data/reference/voivodeships.csv') v
    ON s.voivodeship_code = v.voivodeship_code
WHERE age_at_registration IS NOT NULL
GROUP BY v.voivodeship_name
ORDER BY median_age DESC