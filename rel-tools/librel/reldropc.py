# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-dropc,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import sys

from .args import transput_args
from .args import BadData
from .names import makenames
from .data import readhead, groups

def parsearguments(argv, *, prog = None):
    description = '''

    Drop the specified fields, with count of each remaining record.
    The order of the remaining fields is what it happened to be.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--field', '-f', metavar = 'name*',
                        action = 'append', default = [],
                        help = '''

                        fields to drop, can be separated by commas or
                        spaces, or option can be repeated

                        ''')

    parser.add_argument('--count', '-c', metavar = 'name',
                        required = True,
                        help = '''

                        field name for the count, different from any
                        remaining name

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):

    key = makenames(args.field)
    [count] = makenames([args.count]) # sanity clause

    head = readhead(ins, old = key)
    key = [name for name in head if name not in key]
    if count in key:
        raise BadData('count is old: ' + count.decode('UTF-8'))

    ous.write(b'\t'.join(key))
    key and ous.write(b'\t')
    ous.write(count)
    ous.write(b'\n')

    data = groups(ins, head = head, key = tuple(map(head.index, key)))
    for k, g in data:
        ous.write(b'\t'.join(k))
        key and ous.write(b'\t')
        ous.write(str(sum(1 for r in g)).encode('UTF-8'))
        ous.write(b'\n')
