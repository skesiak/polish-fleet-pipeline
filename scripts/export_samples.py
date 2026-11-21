"""Export CSV samples from the fleet database for profiling tests."""

from pathlib import Path
import duckdb

OUT_DIR = Path("data/samples")
OUT_DIR.mkdir(parents=True, exist_ok=True)
VOIVODESHIPS = ["02", "04", "06", "08", "10", "12", "14", "16",
                "18", "20", "22", "24", "26", "28", "30", "32"]
ROW_LIMIT = 1000  # set to None for the full export used in the GIL measurement

with duckdb.connect("fleet.duckdb", read_only=True) as con:
    for code in VOIVODESHIPS:
        out_path = OUT_DIR / f"vehicles_{code}.csv"
        limit = f"LIMIT {ROW_LIMIT}" if ROW_LIMIT else ""
        con.execute(f"""
            COPY (SELECT * FROM stg_vehicles WHERE voivodeship_code = '{code}' {limit})
            TO '{out_path}' (HEADER, DELIMITER ',')
        """)
        print(f"{out_path} done")