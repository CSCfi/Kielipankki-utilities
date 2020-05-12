# -*- mode: Python; -*-

# Implementation of a command-line tool rel-tools/rel-from,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import sys

from librel.args import transput_args
from librel.args import BadData
from librel.names import makenames, fillnames, checknames
from librel.data import records

def parsearguments(argv, *, prog = None):
    description = '''

    Make a relation from observed values by adding a head of names and
    either tagging the records with a running number or omitting
    duplicates. Fill out the head with names of the form vK (0-based)
    to match the first record, if any.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--field', '-f', metavar = 'name*',
                        action = 'append', default = [],
                        help = '''

                        field names to use, can be separated by commas
                        or spaces, or option can be repeated

                        ''')

    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument('--tag', '-t', metavar = 'name',
                       help = '''

                       tag field name (append to each input record a
                       running number, starting at 1)

                       ''')
    group.add_argument('--unique', '-u', action = 'store_true',
                       help = '''

                       ensure unique records by ignoring duplicates
                       (implies sorting)

                       ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):

    head = makenames(args.field)
    [tag] = (args.tag and makenames([args.tag])) or [None]

    data = records(ins, head = None, unique = args.unique)

    first = next(data, None)
    if first is not None:
        fillnames(head, len(first))
        if len(first) < len(head):
            raise BadData('too many names: {} fields, {} names'
                          .format(len(first), len(head)))

    checknames(head)
    if tag and tag in head:
        raise BadData('tag is in head: ' + tag.decode('UTF-8'))

    ous.write(b'\t'.join(head))
    tag and ous.write(b'\t')
    tag and ous.write(tag)
    ous.write(b'\n')

    if first is None: return

    ous.write(b'\t'.join(first))
    tag and ous.write(b'\t')
    tag and ous.write(b'1')
    ous.write(b'\n')

    def check(r, n = len(head)):
        if len(r) == n: return
        raise BadData('different number of fields: {} fields, {} names'
                      .format(len(record), len(head)))

    if args.unique:
        for r in data:
            check(r)
            ous.write(b'\t'.join(r))
            ous.write(b'\n')
    else:
        for k, r in enumerate(data, start = 2):
            check(r)
            ous.write(b'\t'.join(r))
            ous.write(b'\t')
            ous.write(str(k).encode('UTF-8'))
            ous.write(b'\n')
