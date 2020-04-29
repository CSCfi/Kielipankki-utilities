'''Support library for rel tools (relation tools).

Record cache is for caching a group records for repeated iteration in
join-family operations, using backing store (aka a temporary file) to
hold remaining records when the group is too large for the in-memory
cache.

'''

from itertools import islice
from tempfile import mkstemp

import os

from .data import records

class Cache():

    '''Provides an iterable cache of a group rel-tools records that also
    knows its length (number of records currently in the cache).

    Creates a temp file if cache limit is exceeded. Reuses the same
    temp file. The release() method removes the temp file when the
    cache is no longer needed.

    Warning! Existing iterators over the cache become invalid when a
    new group is cached. Best not to keep iterators around.

    '''

    def __init__(self, limit):
        self._limit_ = limit
        self._cache_ = []
        self._store_ = None
        self._count_ = None # no group yet

    def cache(self, group):
        self._cache_[:] = islice(group, self._limit_)
        self._count_ = len(self._cache_)
        if self._count_ < self._limit_:
            return

        if self._store_ is None:
            fd, self._store_ = mkstemp(prefix = 'cache-', suffix = '.tmp')
            os.close(fd)

        with open(self._store_, 'wb') as ous:
            for r in group:
                ous.write(b'\t'.join(r))
                ous.write(b'\n')
                self._count_ += 1

    def __len__(self):
        if self._count_ is None:
            raise ValueError('cache contains no group')
        return self._count_

    def __iter__(self):
        if self._count_ is None:
            raise ValueError('cache contains no group')

        def it():
            yield from self._cache_
            if self._count_ < self._limit_: return
            yield from records(open(self._store_, 'rb'))

        return it()

    def release(self):
        if self._store_ is not None:
            os.remove(self._store_)
        self._cache_[:] = ()
        self._count_ = None
