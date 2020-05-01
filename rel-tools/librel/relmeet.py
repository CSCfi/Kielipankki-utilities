# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-meet,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

from .args import transput_args
from .args import BadData
from .names import makenames
from .data import readhead, groups

def parsearguments(argv, *, prog = None):
    description = '''

    Intersection of two or more relations of the same type. The order
    of the fields is what it happened to be in the first relation.
    Called "meet" because "intersection" is long.

    '''

    parser = transput_args(description = description, summing = True)

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    args.tag = None # sumfile makes one up

    return args

def main(args, ins, ous):

    # transput arranges so that all input records are in ins, with
    # tags of origin (so ins already is the sum) at end - key (without
    # the tag) is in every input relation if group contains as many
    # records as there are input relations, which is two more than
    # args.rest

    m = 2 + len(args.rest) # infile, inf2, rest

    head = readhead(ins)
    ous.write(b'\t'.join(head[:len(head) - 1])) # drop tag
    ous.write(b'\n')
    for k, g in groups(ins, head = head, key = tuple(range(len(head) - 1))):
        if sum(1 for r in g) == m:
            ous.write(b'\t'.join(k))
            ous.write(b'\n')

    return 0
