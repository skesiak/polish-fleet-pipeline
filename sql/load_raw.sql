DROP TABLE IF EXISTS raw_vehicles;

CREATE TABLE raw_vehicles AS
SELECT
    record.id AS vehicle_id,
    record.attributes.marka AS brand,
    record.attributes.model AS model,
    record.attributes."rodzaj-pojazdu" AS vehicle_type,
    record.attributes."podrodzaj-pojazdu" AS vehicle_subtype,
    record.attributes."pochodzenie-pojazdu" AS origin,
    record.attributes."rok-produkcji" AS production_year,
    record.attributes."data-pierwszej-rejestracji-w-kraju" AS first_registration_date,
    record.attributes."rodzaj-paliwa" AS fuel_type,
    record.attributes."rodzaj-pierwszego-paliwa-alternatywnego" AS alt_fuel_type,
    record.attributes."pojemnosc-skokowa-silnika" AS engine_capacity,
    record.attributes."moc-netto-silnika" AS engine_power,
    record.attributes."masa-wlasna" AS curb_weight,
    record.attributes."rejestracja-powiat" AS county,
    record.attributes."wojewodztwo-kod" AS voivodeship_code,
    filename AS source_file
FROM (
    SELECT unnest(data) AS record, filename
    FROM read_json_auto('data/raw/pojazdy_*.json', filename=true)
);