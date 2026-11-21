"""Run the profiler sequentially, with threads, or with processes."""

import logging
from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from threading import Lock

from profiler.decorators import benchmark
from profiler.profiling import hash_one_file, profile_one_file

logger = logging.getLogger(__name__)


class ProfileAccumulator:
    """Thread-safe accumulator merging per-file profiles into one summary."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.files = 0
        self.rows = 0
        self.empty: dict[str, int] = {}
        self.invalid_periods = 0


    def add(self, result: dict) -> None:
        """Merge one file's profile into the running totals."""
        with self._lock:
            self.files += 1
            self.rows += result["rows"]
            self.invalid_periods += result["invalid_periods"]
            for column, count in result["empty"].items():
                self.empty[column] = self.empty.get(column, 0) + count

@benchmark(repeats=3)
def run_sequential(paths: Iterable[Path]) -> ProfileAccumulator:
    """Profile every file one after another in a single thread."""
    acc = ProfileAccumulator()
    for path in paths:
        acc.add(profile_one_file(path))
    return acc

@benchmark(repeats=3)
def run_threads(paths: Iterable[Path], workers: int = 4) -> ProfileAccumulator:
    """Profile files concurrently using a thread pool."""
    acc = ProfileAccumulator()

    def work(path):
        acc.add(profile_one_file(path))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        list(executor.map(work, paths))

    return acc

@benchmark(repeats=3)
def run_processes(paths: Iterable[Path], workers: int = 4) -> ProfileAccumulator:
    """Profile files in parallel using separate processes."""
    acc = ProfileAccumulator()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for result in executor.map(profile_one_file, paths):
            acc.add(result)
    return acc

@benchmark(repeats=3)
def run_hash(paths: Iterable[Path], mode: str = "sequential", workers: int = 4) -> list[str]:
    """Hash every file in the given mode: sequential, threads or processes."""
    if mode == "sequential":
        return [hash_one_file(path) for path in paths]

    executor_class = ThreadPoolExecutor if mode == "threads" else ProcessPoolExecutor
    with executor_class(max_workers=workers) as executor:
        return list(executor.map(hash_one_file, paths))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    paths = sorted(Path("data/samples").glob("*.csv"))

    acc = run_sequential(paths)
    print(f"sequential: {acc.files} files, {acc.rows} rows, {acc.invalid_periods} invalid")

    acc = run_threads(paths)
    print(f"threads:    {acc.files} files, {acc.rows} rows, {acc.invalid_periods} invalid")

    acc = run_processes(paths)
    print(f"processes:  {acc.files} files, {acc.rows} rows, {acc.invalid_periods} invalid")

    for mode in ("sequential", "threads", "processes"):
        print(f"--- hash, {mode}")
        run_hash(paths, mode=mode)