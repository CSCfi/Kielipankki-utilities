#! /usr/bin/env python3
# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-order,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import sys

from .args import transput_args
from .args import BadData
from .names import makenames
from .data import getter, readhead, records

def parsearguments(argv, *, prog = None):
    description = '''

    Put the specified fields of a relation in the specified order,
    followed by any remaining fields in whatever order they happened
    to be before.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--field', '-f', metavar = 'name*',
                        action = 'append', default = [],
                        help = '''

                        fields desired to be in order before others,
                        can be separated by commas or spaces, or
                        option can be repeated

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):

    order = makenames(args.field)

    head = readhead(ins, old = order)

    order += [name for name in head if name not in order]

    ous.write(b'\t'.join(order))
    ous.write(b'\n')

    permute = getter(tuple(map(head.index, order)))
    data = records(ins, head = head)
    for record in data:
        if len(record) == len(head):
            ous.write(b'\t'.join(permute(record)))
            ous.write(b'\n')
        else:
            raise BadData('different number of fields: {} fields, {} names'
                          .format(len(record), len(head)))
