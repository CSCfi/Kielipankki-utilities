# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-sans,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

from .args import transput_args
from .args import BadData
from .names import makenames
from .data import readhead, groups

def parsearguments(argv, *, prog = None):
    description = '''

    Difference of two or more relations of the same type: records that
    are only in the first relation. The order of the fields is what it
    happened to be in the first relation. Called "sans" because
    "difference" is long.

    '''

    parser = transput_args(description = description, summing = True)

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    args.tag = None # sumfile makes one up

    return args

def main(args, ins, ous):

    # transput arranges so that all input records are in ins, with
    # tags of origin (so ins already is the sum) at end - key (without
    # the tag) is only in the first relation if group consists of one
    # record that is tagged (in the last field) with origin 0

    head = readhead(ins)
    ous.write(b'\t'.join(head[:len(head) - 1])) # drop tag
    ous.write(b'\n')
    for k, g in groups(ins, head = head, key = tuple(range(len(head) - 1))):
        r = next(g)
        if next(g, None) is None and r[-1] == b'0':
            ous.write(b'\t'.join(k))
            ous.write(b'\n')

    return 0
