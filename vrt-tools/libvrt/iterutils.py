
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
