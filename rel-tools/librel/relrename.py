# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-rename,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import sys

from .args import transput_args
from .args import BadData
from .names import makerenames, checknames
from .data import readhead, records

def parsearguments(argv, *, prog = None):
    description = '''

    Rename some fields of a relation.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--map', '-m', metavar = 'old=new*',
                        dest = 'mapping',
                        action = 'append', default = [],
                        help = '''

                        desired mappings of an old name to new (which
                        may also be an old name), can be separated by
                        commas or spaces, or option can be repeated

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):

    mapping = makerenames(args.mapping)

    head = readhead(ins, old = mapping.keys())

    newhead = [mapping.get(old, old) for old in head]
    if len(set(newhead)) < len(newhead):
        bag = sorted(set(n for n in newhead if newhead.count(n) > 1))
        raise BadData('dup in new head: ' + b' '.join(bag).decode('UTF-8'))

    ous.write(b'\t'.join(newhead))
    ous.write(b'\n')

    data = records(ins, head = head)
    for record in data:
        # or could just pass it to cat
        # for speed without another
        # sanity clause
        if len(record) == len(head):
            ous.write(b'\t'.join(record))
            ous.write(b'\n')
        else:
            raise BadData('different number of fields: {} fields, {} names'
                          .format(len(record), len(head)))
