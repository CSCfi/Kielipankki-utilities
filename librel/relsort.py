#! /usr/bin/env python3
# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-sort,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import sys

from .args import transput_args
from .args import BadData
from .names import makenames, fillnames, checknames
from .data import record as torecord, records

def parsearguments(argv, *, prog = None):
    description = '''

    Sort the records in a relation by the specified fields, or by all
    fields in the order they happen to be if no sort-key specified.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--key', '-k', metavar = 'name(s)',
                        action = 'append', default = [],
                        help = '''

                        fields to sort by, can be separated by commas
                        or spaces or option repeated

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):

    key = makenames(args.key)
    checknames(key)

    head = next(ins, None)
    if head is None:
        raise BadData('no head')

    head = torecord(head)
    key = key or head
    bad = [name for name in key if name not in head]
    if bad:
        raise BadData('bad keys: ' + repr(bad))

    ous.write(b'\t'.join(head))
    ous.write(b'\n')

    key = tuple(map(head.index, key))
    data = records(ins, key = key)
    for record in data:
        if len(record) == len(head):
            ous.write(b'\t'.join(record))
            ous.write(b'\n')
        else:
            raise BadData('different number of fields: {} fields, {} names'
                          .format(len(record), len(head)))
