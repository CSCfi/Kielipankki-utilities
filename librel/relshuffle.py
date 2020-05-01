# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-shuffle,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import os
import subprocess

from .args import transput_args
from .data import readhead
from .bins import SORT

def parsearguments(argv, *, prog = None):
    description = '''

    Shuffle the records in a relation.

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

    subprocess.run([ SORT, '--random-sort' ],
                   env = dict(os.environ,
                              LC_ALL = 'C'),
                   stdin = ins,
                   stdout = ous,
                   stderr = None)
