#! /usr/bin/env python3
# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-symm,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

from .args import transput_args
from .args import BadData
from .names import makenames
from .data import readhead, groups

def parsearguments(argv, *, prog = None):
    description = '''

    Symmetric difference of two or more relations of the same type:
    records that are only in one relation. The order of the fields is
    what it happened to be in the first relation. The name may or may
    not be apt.

    '''

    parser = transput_args(description = description, summing = True)

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    args.tag = None # sumfile makes one up

    return args

def main(args, ins, ous):

    # transput arranges so that all input records are in ins, with
    # tags of origin (so ins already is the sum) at end - key (without
    # the tag) is only in one input relation if the group consists of
    # one record.

    # TODO optionally retain tag of origin

    head = readhead(ins)
    ous.write(b'\t'.join(head[:len(head) - 1])) # drop tag
    ous.write(b'\n')
    for k, g in groups(ins, key = tuple(range(len(head) - 1))):
        r = next(g)
        if next(g, None) is None:
            ous.write(b'\t'.join(k))
            ous.write(b'\n')

    return 0
