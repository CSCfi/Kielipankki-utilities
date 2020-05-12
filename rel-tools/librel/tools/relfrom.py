# -*- mode: Python; -*-

# Implementation of a command-line tool rel-tools/rel-from,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import re
import sys

from librel.args import transput_args
from librel.args import BadData
from librel.names import makerenames, makenames, fillnames, checknames
from librel.data import records

def parsearguments(argv, *, prog = None):
    description = '''

    Make a relation from observed values by adding a head of names and
    either tagging the records with a running number or omitting
    duplicates. Fill out the head with names of the form vK (1-based)
    to match the first record, if any.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--map', '-m', metavar = 'old=new*',
                        dest = 'renames',
                        action = 'append', default = [],
                        help = '''

                        map any default field names v1 and so on to a
                        desired name, can be separated by commas or
                        spaces, or option can be repeated

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

    rens = makerenames(args.renames) # vk => whatever, k > 0

    bad = sorted(old for old in rens if not re.match(b'v[1-9][0-9]*', old))
    if bad:
        raise BadData('"old" names not vk: ' +
                      b' '.join(bad).encode('UTF-8'))

    high = max((int(old.strip(b'v')) for old in rens), default = 0)
    head = [
        rens.get(vk, vk)
        for k in range(1, high + 1)
        for vk in ['v{}'.format(k).encode('UTF-8')]
    ]

    # at this point head is ['word', 'v2', 'ref']
    # if rens maps 'v3' to 'ref' and 'v1' to 'word'
    # ([] if rens is {})
    # extended with more 'vk' at any first record

    [tag] = (args.tag and makenames([args.tag])) or [None]

    data = records(ins, head = None, unique = args.unique)

    first = next(data, None)
    if head == [] and first == [b'']:
        # with empty head, [b''] means [],
        # every incoming record must be [b'']
        # to be interpreted as []
        pass
    elif first is None:
        # any head is compatible with an empty relation
        pass
    else:
        # with non-empty first field, or more than one field,
        # an empty head needs filled;
        # with non-empty head, even [b''] means [b'']
        fillnames(head, len(first))
        if len(first) < len(head):
            raise BadData('too many names: {} fields, {} names'
                          .format(len(first), len(head)))

    checknames(head)
    if tag and tag in head:
        raise BadData('tag is in head: ' + tag.decode('UTF-8'))

    ous.write(b'\t'.join(head))
    head and tag and ous.write(b'\t')
    tag and ous.write(tag)
    ous.write(b'\n')

    if first is None: return

    ous.write(b'\t'.join(first))
    head and tag and ous.write(b'\t')
    tag and ous.write(b'1')
    ous.write(b'\n')

    def check(r, n = len(head)):
        if len(r) == n: return
        raise BadData('record length: expected {}: observed {}: {}'
                      .format(n, len(r),
                              repr([v.decode('UTF-8')
                                    for v in r])))

    if head and args.unique:
        for r in data:
            check(r)
            ous.write(b'\t'.join(r))
            ous.write(b'\n')
    elif head:
        for k, r in enumerate(data, start = 2):
            check(r)
            ous.write(b'\t'.join(r))
            ous.write(b'\t')
            ous.write(str(k).encode('UTF-8'))
            ous.write(b'\n')
    elif args.unique:
        for r in data:
            # no field names specified,
            # first record was [b''],
            # interpreted as empty,
            # now another record in a *unique* stream
            raise BadData('no specified names, an empty record: '
                          'record should be empty: ' +
                          repr([v.decode('UTF-8') for v in r]))
    elif True:
        # no field names specified,
        # first record was [b''],
        # interpreted as empty (no fields),
        # so every record must be interpretable as empty
        for k, r in enumerate(data, start = 2):
            if r == [b'']:
                ous.write(str(k).encode('UTF-8'))
                ous.write(b'\n')
            else:
                raise BadData('no specified names, empty first record: '
                              'record should be empty: ' +
                              repr([v.decode('UTF-8') for v in r]))
