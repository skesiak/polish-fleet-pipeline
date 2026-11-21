"""Decorators used across the profiler."""

import functools
import logging
import time

logger = logging.getLogger(__name__)


def timed(func):
    """Log how long the decorated function takes to run."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info("%s took %.3f s", func.__name__, elapsed)
        return result

    return wrapper


def requires_data(method):
    """Raise if the decorated method is called before load()."""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self._profile is None:
            raise RuntimeError(f"{method.__name__}() requires load() to be called first")
        return method(self, *args, **kwargs)

    return wrapper


def benchmark(repeats: int = 3):
    """Run the decorated function repeats times and log the best duration."""

    def decorator(func):
    
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            durations = []
            for _ in range(repeats):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                durations.append(time.perf_counter() - start)
            logger.info("%s: best %.3f s of %d runs", func.__name__, min(durations), repeats)
            return result

        return wrapper

    return decorator