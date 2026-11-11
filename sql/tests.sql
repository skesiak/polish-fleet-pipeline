SELECT 'stg_row_count' AS test,
       CASE WHEN COUNT(*) BETWEEN 3100000 AND 3300000
            THEN 'PASS' ELSE 'FAIL' END AS status
FROM stg_vehicles

UNION ALL

SELECT 'no_duplicate_vehicle_id',
       CASE WHEN COUNT(*) = COUNT(DISTINCT vehicle_id)
            THEN 'PASS' ELSE 'FAIL' END
FROM stg_vehicles

UNION ALL

SELECT 'fact_sum_matches_staging',
       CASE WHEN (SELECT SUM(registrations) FROM fct_registrations_monthly)
                 = (SELECT COUNT(*) FROM stg_vehicles)
            THEN 'PASS' ELSE 'FAIL' END

UNION ALL

SELECT 'voivodeship_period_count',
        CASE WHEN (SELECT COUNT(*) FROM (SELECT DISTINCT voivodeship_code, period FROM stg_vehicles)) = 384
            THEN 'PASS' ELSE 'FAIL' END

UNION ALL

SELECT 'all_voivodeship_codes_matched',
        CASE WHEN (SELECT COUNT(*) FROM stg_vehicles 
            WHERE voivodeship_code NOT IN 
                (SELECT voivodeship_code 
                FROM read_csv_auto('data/reference/voivodeships.csv'))) = 0
            THEN 'PASS' ELSE 'FAIL' END

UNION ALL

-- max observed: 76 years (vintage vehicles are registered too), 100 leaves headroom
SELECT 'age_in_plausible_range',
       CASE WHEN (SELECT COUNT(*) FROM stg_vehicles
                  WHERE age_at_registration < 0 OR age_at_registration > 100) = 0 
            THEN 'PASS' ELSE 'FAIL' END

UNION ALL

-- observed: 0.03-0.09% across all 24 periods
SELECT 'fuel_other_share',
       CASE WHEN COUNT(*) FILTER (WHERE fuel_category = 'other') * 100.0 / COUNT(*) < 0.5 
            THEN 'PASS' ELSE 'FAIL' END
FROM stg_vehicles

UNION ALL

SELECT 'age_null_share',
        CASE WHEN COUNT(*) FILTER (WHERE age_at_registration IS NULL) * 100.0 / COUNT(*) < 0.1
            THEN 'PASS' ELSE 'FAIL' END
FROM stg_vehicles

UNION ALL

-- observed: 1.33% (202407) rising to 4.45% (202606), see README
-- threshold will need raising on future downloads
SELECT 'brand_null_share',
        CASE WHEN COUNT(*) FILTER (WHERE brand IS NULL) * 100.0 / COUNT(*) < 6.0 
            THEN 'PASS' ELSE 'FAIL' END
FROM stg_vehicles

UNION ALL

SELECT 'period_matches_registration_date',
       CASE WHEN COUNT(*) FILTER (
                WHERE period <> strftime(first_registration_date, '%Y%m')) = 0
            THEN 'PASS' ELSE 'FAIL' END
FROM stg_vehicles;