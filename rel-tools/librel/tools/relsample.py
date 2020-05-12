# -*- mode: Python; -*-

# Implementation of a command-line tool rel-tools/rel-sample,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import subprocess
import sys

from librel.args import transput_args
from librel.args import BadData
from librel.names import makenames
from librel.data import getter, readhead, records
from librel.bins import SHUF

def parsearguments(argv, *, prog = None):
    description = '''

    A uniform random sample of a desired number of the records in the
    relation.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--records', '-n', metavar = 'number',
                        type = int, # want *positive*
                        default = 30, # how big is a sample?
                        help = '''

                        desired sample size, defaults to 30 records

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):

    head = readhead(ins)

    ous.write(b'\t'.join(head))
    ous.write(b'\n')
    ous.flush()

    subprocess.run([ SHUF, '--head-count', str(args.records) ],
                   stdin = ins,
                   stdout = ous,
                   stderr = None)
