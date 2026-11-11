#!/usr/bin/env bash
set -euo pipefail

# polish-fleet-pipeline: full rebuild from raw JSON files to analytical tables.
# Usage: ./run.sh

DB="fleet.duckdb"

echo " 1/4 checking raw data "

mkdir -p data/raw
RAW_COUNT=$(find data/raw -maxdepth 1 -name '*.json' | wc -l | tr -d ' ')

if [ "$RAW_COUNT" -eq 0 ]; then
    echo "No raw data found in data/raw/"
    echo "Run the collector first: python src/fetch_cepik.py"
    exit 1
fi

echo "Found $RAW_COUNT JSON files"

echo " 2/4 removing old database "

rm -f "$DB"

echo " 3/4 building tables "

duckdb "$DB" -f sql/load_raw.sql
echo "  raw_vehicles done"

duckdb "$DB" -f sql/stg_vehicles.sql
echo "  stg_vehicles done"

duckdb "$DB" -f sql/fct_registrations_monthly.sql
echo "  fct_registrations_monthly done"

echo " 4/4 running data quality tests ==="

RESULTS=$(duckdb "$DB" -csv -f sql/tests.sql)
echo "$RESULTS"

if echo "$RESULTS" | grep -q FAIL; then
    echo ""
    echo "Data quality tests FAILED. Database left in place for inspection."
    exit 1
fi

echo ""
echo "All data quality tests passed. Database: $DB"