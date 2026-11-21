"""Regex validation rules for profiled data."""

import re
from collections.abc import Iterable

PERIOD_PATTERN = re.compile(r"(?P<year>\d{4})(?P<month>0[1-9]|1[0-2])")

FILENAME_PATTERN = re.compile(r"vehicles_(?P<code>\d{2})\.csv")


def match_pattern(value: str, pattern: re.Pattern) -> dict[str, str] | None:
    """Return the pattern's named groups for value, or None if it does not match."""
    match = pattern.fullmatch(value)
    if match is None:
        return None
    return match.groupdict()


def count_invalid(values: Iterable[str], pattern: re.Pattern) -> int:
    """Count how many values do not match the pattern."""
    count = 0
    for value in values:
        if match_pattern(value, pattern) is None:
            count += 1
    return count


if __name__ == "__main__":
    print(match_pattern("202503", PERIOD_PATTERN))
    print(match_pattern("202513", PERIOD_PATTERN))
    print(match_pattern("", PERIOD_PATTERN))
    print(match_pattern("vehicles_14.csv", FILENAME_PATTERN))
    print(count_invalid(["202501", "202513", "abc", "202512"], PERIOD_PATTERN))

