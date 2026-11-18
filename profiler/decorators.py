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