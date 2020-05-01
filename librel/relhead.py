# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-head,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import subprocess

from .args import transput_args
from .data import readhead
from .bins import HEAD

def parsearguments(argv, *, prog = None):
    description = '''

    The records that happen to be "first" in the body of a
    relation. In theory, nonsense. (Pun not intended, either.)

    '''

    parser = transput_args(description = description)

    parser.add_argument('--records', '-n', metavar = '(-)number',
                        type = int, default = 10,
                        help = '''

                        Keep the given number of "first" records,
                        default 10. With the minus sign, omit the
                        given number of "last" records.

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):

    head = readhead(ins)

    ous.write(b'\t'.join(head))
    ous.write(b'\n')
    ous.flush()

    subprocess.run([ HEAD, '--lines', str(args.records) ],
                   stdin = ins,
                   stdout = ous,
                   stderr = None)

    return 0
