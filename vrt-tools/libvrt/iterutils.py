
"""
Module libvrt.iterutils

This module contains utility functions for iterables.
"""


from collections import Counter
from itertools import chain


def find_duplicates(*iters):
    """Return list of items occurring more than once in iterables *iters."""
    counts = Counter(chain(*iters))
    return [item for item, cnt in counts.items() if cnt > 1]


def make_unique(*iters):
    """Return a list of items in iterables *iters, each only once.

    The result contains the items in the order of their first occurrence.
    """
    seen = set()
    result = []
    for item in chain(*iters):
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
