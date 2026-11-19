import csv
from collections.abc import Iterable, Iterator
from pathlib import Path

"""Streaming readers for CSV files."""

"""Yield rows from a single CSV file as dictionaries."""
def iter_rows(path: Path) -> Iterator[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

"""Yield rows from every CSV file in turn."""
def iter_all_rows(paths: Iterable[Path]) -> Iterator[dict[str, str]]:
    for path in paths:
        yield from iter_rows(path)

