"""Profile CSV files: row counts, empty values and distinct values per column."""

import hashlib
import logging
from collections.abc import Iterable
from itertools import chain
from pathlib import Path

from profiler.decorators import timed
from profiler.reader import iter_rows, iter_all_rows
from profiler.validation import FILENAME_PATTERN, PERIOD_PATTERN, match_pattern

CHUNK_SIZE = 1024 * 1024


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


def profile_one_file(path: Path) -> dict:
    """Profile a single CSV file and return a small, picklable summary."""

    groups = match_pattern(path.name, FILENAME_PATTERN)
    code = groups["code"] if groups else "unknown"

    row_count = 0
    empty_values = {}
    wrong_count = 0

    for row in iter_rows(path):
        row_count += 1
        if match_pattern(row["period"], PERIOD_PATTERN) is None:
            wrong_count += 1
        for column, value in row.items():
            if value == "":
                empty_values[column] = empty_values.get(column, 0) + 1

    return {
        "code": code,
        "rows": row_count,
        "empty": empty_values,
        "invalid_periods": wrong_count,
    }


def hash_one_file(path: Path, rounds: int = 5) -> str:
    """Return the SHA-256 digest of a file, hashed in chunks, repeated rounds times."""
    for _ in range(rounds):
        digest = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    rows, empty, distinct = profile_rows([Path("data/samples/vehicles_02.csv")])
    print(f"{rows} rows")
    for column, count in empty.items():
        print(f"  {column}: {count} empty, {len(distinct[column])} distinct")
    print(profile_one_file(Path("data/samples/vehicles_02.csv")))
    