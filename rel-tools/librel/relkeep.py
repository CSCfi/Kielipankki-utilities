# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-keep,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import sys

from .args import transput_args
from .names import makenames
from .data import readhead, groups

def parsearguments(argv, *, prog = None):
    description = '''

    Keep only the specified fields. Additionally, produce those fields
    in the specified order.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--field', '-f', metavar = 'name*',
                        action = 'append', default = [],
                        help = '''

                        fields to keep, can be separated by commas or
                        spaces, or option can be repeated

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):

    key = makenames(args.field)

    head = readhead(ins, old = key)

    ous.write(b'\t'.join(key))
    ous.write(b'\n')

    key = tuple(map(head.index, key))
    data = groups(ins, head = head, key = key)
    for k, g in data:
        ous.write(b'\t'.join(k))
        ous.write(b'\n')
