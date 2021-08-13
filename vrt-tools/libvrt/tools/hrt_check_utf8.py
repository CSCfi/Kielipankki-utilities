# -*- mode: Python; -*-

'''Implementation of hrt-check-utf8.'''

from libvrt.args import BadData, nat
from libvrt.args import transput_args
from libvrt.check import setup_text
from libvrt.check import error, warn, info

import re

def parsearguments(args, *, prog = None):

    description = '''

    Report on the valid UTF-8 encoding or otherwise of an "HRT"
    document.

    '''

    parser = transput_args(description = description,
                           inplace = False)

    group = parser.add_mutually_exclusive_group()
    # to have --warning, --error some day, maybe
    group.add_argument('--info', action = 'store_true',
                        help = '''

                        Include merely informative messages (if any).

                        ''')
    
    parser.add_argument('--limit', metavar = 'N',
                        default = 10,
                        type = nat,
                        help = '''

                        Exit after reporting N (10) lines that fail.

                        ''')
    parser.add_argument('--no-limit', action = 'store_true',
                        dest = 'no_limit',
                        help = '''

                        Report every line that fails. Overrides any
                        limit.

                        ''')

    args = parser.parse_args()
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):
    '''Transput HRT input stream in ins to TSV report in ous.

    '''

    setup_text(ous)

    failures = 0
    for k, line in enumerate(ins, start = 1):
        try:
            text = line.decode('UTF-8')
        except UnicodeDecodeError as exn:
            error(k, 'code', 'failed to decode line as UTF-8')
            failures += 1

        if failures >= args.limit and not args.no_limit:
            exit(0)

    if args.info and not failures:
        info(0, 'code', 'every line decoded as UTF-8')
    
