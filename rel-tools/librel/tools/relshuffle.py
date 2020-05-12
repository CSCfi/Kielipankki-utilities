# -*- mode: Python; -*-

# Implementation of a command-line tool rel-tools/rel-shuffle,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

# import os
import subprocess

from librel.args import transput_args
from librel.data import readhead
from librel.bins import SHUF

def parsearguments(argv, *, prog = None):
    description = '''

    Permute the records in a relation.

    '''

    parser = transput_args(description = description)

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):

    head = readhead(ins)

    ous.write(b'\t'.join(head))
    ous.write(b'\n')
    ous.flush()

    subprocess.run([ SHUF ],
                   stdin = ins,
                   stdout = ous,
                   stderr = None)
