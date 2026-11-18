import csv
from pathlib import Path


def profile_file(path: Path) -> tuple[int, dict[str, int], dict[str, set[str]]]:
    """Count rows and empty values per column in a CSV file."""


    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        empty_counts = {column: 0 for column in columns}
        distinct_values = {column: set() for column in columns}
        row_count = 0
        

        for row in reader:
            row_count += 1
            for column in columns:
                value = row[column]
                if value == "":
                    empty_counts[column] += 1
                else:
                    distinct_values[column].add(value)

    return row_count, empty_counts, distinct_values


if __name__ == "__main__":
    rows, empty, distinct = profile_file(Path("data/samples/vehicles_02.csv"))
    print(f"{rows} rows")
    for column, count in empty.items():
        print(f"  {column}: {count} empty, {len(distinct[column])} distinct")