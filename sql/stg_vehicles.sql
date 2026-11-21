DROP TABLE IF EXISTS stg_vehicles;

CREATE TABLE stg_vehicles AS
SELECT
    vehicle_id,
    brand,
    model,
    vehicle_type,
    vehicle_subtype,
    CASE
        WHEN origin = 'NOWY ZAKUPIONY W KRAJU'  THEN 'new_domestic'
        WHEN origin = 'NOWY IMPORT INDYW'       THEN 'new_import'
        WHEN origin = 'UŻYW. IMPORT INDYW'      THEN 'used_import'
        WHEN origin = 'UŻYW. ZAKUPIONY W KRAJU' THEN 'used_domestic'
        ELSE 'other'
    END AS origin_category,
    CASE
        WHEN fuel_type = 'BENZYNA'       AND alt_fuel_type = 'ENERGIA ELEKTRYCZNA' THEN 'hybrid_petrol'
        WHEN fuel_type = 'OLEJ NAPĘDOWY' AND alt_fuel_type = 'ENERGIA ELEKTRYCZNA' THEN 'hybrid_diesel'
        WHEN fuel_type = 'ENERGIA ELEKTRYCZNA'                                     THEN 'electric'
        WHEN alt_fuel_type = 'GAZ PŁYNNY PROPAN-BUTAN'                             THEN 'lpg'
        WHEN fuel_type = 'BENZYNA'                                                 THEN 'petrol'
        WHEN fuel_type = 'OLEJ NAPĘDOWY'                                           THEN 'diesel'
        ELSE 'other'
    END AS fuel_category,
    TRY_CAST(production_year AS INTEGER) AS production_year,
    TRY_CAST(first_registration_date AS DATE) AS first_registration_date,
    TRY_CAST(engine_capacity AS DOUBLE) AS engine_capacity,
    TRY_CAST(engine_power AS DOUBLE) AS engine_power,
    TRY_CAST(curb_weight AS INTEGER) AS curb_weight,
    county,
    voivodeship_code,
    source_file,
    regexp_extract(source_file, '_(\d{6})_', 1) AS period,
    CASE
        WHEN TRY_CAST(production_year AS INTEGER) < 1950 THEN NULL
        ELSE EXTRACT(YEAR FROM TRY_CAST(first_registration_date AS DATE))
             - TRY_CAST(production_year AS INTEGER)
    END AS age_at_registration
FROM raw_vehicles
WHERE vehicle_type IN ('SAMOCHÓD OSOBOWY', 'SAMOCHÓD CIĘŻAROWY')
QUALIFY ROW_NUMBER() OVER (PARTITION BY vehicle_id ORDER BY source_file) = 1;