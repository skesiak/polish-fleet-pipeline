"""Profile CSV files: row counts, empty values and distinct values per column."""
import logging
from collections.abc import Iterable
from itertools import chain
from pathlib import Path

from profiler.decorators import timed
from profiler.reader import iter_all_rows

@timed
def profile_rows(paths: Iterable[Path]) -> tuple[int, dict[str, int], dict[str, set[str]]]:
    """Count rows, empty values and distinct non-empty values per column.

    Empty strings are treated as missing and excluded from the distinct sets.
    """
    rows = iter_all_rows(paths)
    first = next(rows, None)

    if first is None:
        return 0, {}, {}

    columns = list(first)
    rows = chain([first], rows)

    empty_counts = {column: 0 for column in columns}
    distinct_values = {column: set() for column in columns}
    row_count = 0
        
    for row in rows:
        row_count += 1
        for column in columns:
            value = row[column]
            if value == "":
                empty_counts[column] += 1
            else:
                distinct_values[column].add(value)

    return row_count, empty_counts, distinct_values


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    rows, empty, distinct = profile_rows([Path("data/samples/vehicles_02.csv")])
    print(f"{rows} rows")
    for column, count in empty.items():
        print(f"  {column}: {count} empty, {len(distinct[column])} distinct")