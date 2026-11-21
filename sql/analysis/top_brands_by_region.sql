WITH brand_counts AS (
    SELECT
        v.voivodeship_name,
        s.brand,
        COUNT(*) AS registrations
    FROM stg_vehicles s
    JOIN read_csv_auto('data/reference/voivodeships.csv') v
        ON s.voivodeship_code = v.voivodeship_code
    WHERE s.age_at_registration >= 10
      AND s.brand IS NOT NULL
    GROUP BY v.voivodeship_name, s.brand
)
SELECT
    voivodeship_name,
    brand,
    registrations,
    ROUND(registrations * 100.0 / SUM(registrations) OVER (PARTITION BY voivodeship_name), 1) AS pct_in_voivodeship,
    ROW_NUMBER() OVER (PARTITION BY voivodeship_name ORDER BY registrations DESC) AS brand_rank
FROM brand_counts
QUALIFY brand_rank <= 5
ORDER BY voivodeship_name, brand_rank;