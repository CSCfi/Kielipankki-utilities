#! /usr/bin/env python3
# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-from,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import sys

from .args import transput_args
from .args import BadData
from .names import makenames, fillnames, checknames
from .data import records

def parsearguments(argv, *, prog = None):
    description = '''

    Make a relation output from observed values by adding a head of
    names and either distinguishing the records by a counter (default)
    or omitting duplicates. Append generated names of the form "vK"
    with 1-based field number K if more fields than specified names
    are encountered.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--names', '-n', metavar = 'name(s)',
                        dest = 'names',
                        action = 'append', default = [],
                        help = '''

                        field names to use, can be separated by commas
                        or spaces or option repeated, counter name
                        first, if any

                        ''')

    parser.add_argument('--unique', '-u', action = 'store_true',
                        help = '''

                        ensure unique records by omitting duplicates
                        (implies sorting)

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):

    names = makenames(args.names)

    if args.unique:
        data = records(ins, head = None, unique = True)
    else:
        data = (
            [str(k).encode('utf-8')] + r
            for k, r in enumerate(records(ins, head = None, ), start = 1)
        )

    first = next(data, None)
    if first is not None:
        fillnames(names, len(first))
        if len(first) < len(names):
            raise BadData('too many names: {} fields, {} names'
                          .format(len(first), len(names)))

    checknames(names)

    ous.write(b'\t'.join(names))
    ous.write(b'\n')

    if first is None: return

    ous.write(b'\t'.join(first))
    ous.write(b'\n')

    for record in data:
        if len(record) == len(names):
            ous.write(b'\t'.join(record))
            ous.write(b'\n')
        else:
            raise BadData('different number of fields: {} fields, {} names'
                          .format(len(record), len(names)))
