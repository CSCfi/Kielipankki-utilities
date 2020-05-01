# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-sample,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import sys

from .args import transput_args
from .args import BadData
from .names import makenames
from .data import getter, readhead, records
from .sample import fill

def parsearguments(argv, *, prog = None):
    description = '''

    A uniform random sample of a desired number of the records in the
    relation, optionally tagged with whatever their 1-based position
    happened to be.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--records', '-n', metavar = 'number',
                        type = int, # want *positive*
                        default = 30, # how big is a sample?
                        help = '''

                        desired sample size, defaults to 30 records

                        ''')

    parser.add_argument('--tag', '-t', metavar = 'name',
                        help = '''

                        name for a new field to tag the records in the
                        sample with their (theoretically meaningless)
                        position in the original relation

                        ''')

    parser.add_argument('--seed', '-s', metavar = 'string',
                        help = '''

                        random seed to get a repeatable sample,
                        defaults to the state of the environment

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):

    [tag] = makenames([args.tag]) if args.tag else [None]
    head = readhead(ins, new = [tag] if tag else ())

    pool = list(range(args.records))
    fill(pool, source = ins, seed = args.seed)

    ous.write(b'\t'.join(head))
    head and tag and ous.write(b'\t')
    tag and ous.write(tag)
    ous.write(b'\n')

    for k, line in pool:
        line = line.rstrip(b'\r\n')
        ous.write(line)
        head and tag and ous.write(b'\t')
        tag and ous.write(str(k).encode('UTF-8'))
        ous.write(b'\n')
