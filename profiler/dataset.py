"""Dataset: a set of CSV files to profile, with a suspect-column threshold."""

from collections.abc import Iterable
from pathlib import Path

from profiler.decorators import requires_data
from profiler.profiling import profile_rows

class Dataset:
    def __init__(self, paths: Iterable[Path], empty_threshold: float = 0.05) -> None:
        self.paths = list(paths)
        self.empty_threshold = empty_threshold
        self._profile = None

    @property
    def empty_threshold(self) -> float:
        """Share of empty values above which a column is reported as suspect."""
        return self._empty_threshold

    @empty_threshold.setter
    def empty_threshold(self, value: float) -> None:
        if not 0 <= value <= 1:
            raise ValueError(f"empty_threshold must be between 0 and 1, got {value}")
        self._empty_threshold = value

    def load(self):
        self._profile = profile_rows(self.paths)

    @requires_data
    def suspect_columns(self) -> list[str]:
        """Return columns whose share of empty values exceeds the threshold."""
        row_count, empty_counts, _ = self._profile
        return [
            column
            for column, count in empty_counts.items()
            if count / row_count > self.empty_threshold
        ]

