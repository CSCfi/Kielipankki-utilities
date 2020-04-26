'''Support library for rel-tools (relation tools).

Heavily relies on GNU sort, or possibly another implementation of
sort(1) that has the same options -- are they Posix?

'''

from itertools import groupby
from operator import itemgetter
from subprocess import Popen, PIPE

import os

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

def records(ins, *, unique = False, key = ()):
    '''Generate each record from the (binary) input stream.

    Optionally sort the input to generate unique records.
    Optionally sort the input by key fields.
    The key is specified as a tuple of 0-based indices.

    '''

    if not unique and not key:
        return (record(line) for line in ins)

    options = []
    options.append('--unique' if unique else '--stable')
    if key:
        options.append('--field-separator=\t')
        options.extend('--key={k},{k}'.format(k = k + 1) for k in key)

    proc = Popen([ 'sort' ] + options,
                 env = dict(os.environ,
                            LC_ALL='C'),
                 stdin = ins,
                 stdout = PIPE,
                 stderr = None)

    # TODO ensure termination how

    return (record(line) for line in proc.stdout)

def groups(ins, *, key):
    '''Generate from the binary input stream each tuple of key values
    together with the group of records that agree on the key.

    The records are sorted on the key (stable).
    The key is specified as a tuple of 0-based indices.

    '''

    return groupby(records(ins, key = key), key = getter(key))
