'''Support library for rel-tools (relation tools).

Heavily relies on GNU sort, or possibly another implementation of
sort(1) that has the same options -- are they Posix?

'''

from itertools import groupby
from operator import itemgetter
from subprocess import Popen, PIPE

import os

from .bad import BadData
from .names import checknames
from .bins import SORT

def record(line):
    '''Split a tab-separated (binary) line into its fields.'''

    return line.rstrip(b'\r\n').split(b'\t')

def getter(key):
    '''Returns a getter to get the key values of a record in a tuple.

    The key is specified as a tuple of 0-based indices.

    '''

    if len(key) == 0:
        return lambda record : ()
    elif len(key) == 1:
        get = itemgetter(*key)
        return lambda record : (get(record),)
    else:
        return itemgetter(*key)

def records(ins, *, head, unique = False, key = ()):
    '''Generate each record from the (binary) input stream.

    Set head to None when not available, as in rel-from.
    An empty head indicates special reading TODO. Other
    cases could also support checking that input records
    are of the expected length TODO? Reading head had to
    be separate from reading body because head is needed
    to compute sorting and grouping keys.

    Optionally sort the input to generate unique records.
    Optionally sort the input by key fields.
    The key is specified as a tuple of 0-based indices.

    '''

    if head is not None and len(head) == 0:
        # TODO (otherwise an empty input line is taken to be a record
        # of one field that happens to contain the empty string)
        return empty_records(ins)

    if not unique and not key:
        return (record(line) for line in ins)

    options = []
    options.append('--unique' if unique else '--stable')
    if key:
        options.append('--field-separator=\t')
        options.extend('--key={k},{k}'.format(k = k + 1) for k in key)

    proc = Popen([ SORT ] + options,
                 env = dict(os.environ,
                            LC_ALL='C'),
                 stdin = ins,
                 stdout = PIPE,
                 stderr = None)

    # TODO ensure termination how - run by whatever consumes generator

    return (record(line) for line in proc.stdout)

def empty_records(ins):
    for line in ins:
        line = line.rstrip(b'\r\n')
        if line:
            raise BadData('too many fields')
        yield []

def groups(ins, *, head, key):
    '''Generate from the binary input stream each tuple of key values
    together with the group of records that agree on the key.

    An empty head indicates special reading. See records.

    The records are sorted on the key (stable).
    The key is specified as a tuple of 0-based indices.

    '''

    return groupby(records(ins, head = head, key = key),
                   key = getter(key))

def readhead(ins, *, old = (), new = ()):
    '''Return the assumed-first tab-separated line from binary stream.
    Raise an exception if the fields are not valid names, or if any of
    the specified old names is not in the head, or if any of the
    specified new is in the head.

    '''

    line = next(ins, None)
    if line is None:
        raise BadData('no head')

    line = line.rstrip(b'\r\n')
    if line:
        head = record(line)
        checknames(head)
    else:
        # line.split(b'\t') => [b'']
        head = []

    bad = [name for name in old if name not in head]
    if bad:
        raise BadData('not in head: ' + b' '.join(bad).decode('UTF-8'))

    bad = [name for name in new if name in head]
    if bad:
        raise BadData('already in head: ' + b' '.join(bad).decode('UTF-8'))

    return head
