# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-tail,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import subprocess

from .bad import BadData
from .args import transput_args
from .data import readhead
from .bins import TAIL

def parsearguments(argv, *, prog = None):
    description = '''

    The records that happen to be "last" in the body of a relation. In
    theory, nonsense.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--records', '-n', metavar = '(+)number',
                        default = '10',
                        help = '''

                        Keep the given number of "last" records,
                        default 10. With the plus sign, keep the
                        records from the "nth" record to the "end".

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):

    digits = args.records[args.records.startswith('+'):]
    if (any(git not in '0123456789' for git in digits) or
        not digits):
        raise BadData('odd number of records: ' + args.records)

    head = readhead(ins)

    ous.write(b'\t'.join(head))
    ous.write(b'\n')
    ous.flush()

    subprocess.run([ TAIL, '--lines', args.records ],
                   stdin = ins,
                   stdout = ous,
                   stderr = None)

    return 0
