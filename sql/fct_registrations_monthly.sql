DROP TABLE IF EXISTS fct_registrations_monthly;

CREATE TABLE fct_registrations_monthly AS
SELECT
    period,
    voivodeship_code,
    county,
    fuel_category,
    COUNT(*) AS registrations,
    MEDIAN(age_at_registration) AS median_age,
    ROUND(AVG(age_at_registration), 1) AS avg_age,
    COUNT(*) FILTER (WHERE origin_category = 'new_domestic') AS new_domestic_count,
    COUNT(*) FILTER (WHERE origin_category = 'new_import') AS new_import_count,
    COUNT(*) FILTER (WHERE origin_category = 'used_domestic') AS used_domestic_count,
    COUNT(*) FILTER (WHERE origin_category = 'used_import') AS used_import_count
FROM stg_vehicles
GROUP BY period, voivodeship_code, county, fuel_category;