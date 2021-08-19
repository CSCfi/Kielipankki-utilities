# -*- mode: Python; -*-

'''Implementation of hrt-check-shy.

https://en.wikipedia.org/wiki/Soft_hyphen

'''

from libvrt.args import BadData, nat
from libvrt.args import transput_args
from libvrt.check import setup_text
from libvrt.check import error, warn, info

import re

def parsearguments(args, *, prog = None):

    description = '''

    Report on the use of U+00AD, the "soft hyphen" character.

    '''

    parser = transput_args(description = description,
                           inplace = False)

    group = parser.add_mutually_exclusive_group()
    # to have --warning, --error some day, maybe
    group.add_argument('--info', action = 'store_true',
                        help = '''

                        include informative messages (if any)

                        ''')
    
    parser.add_argument('--limit', metavar = 'N',
                        default = 10,
                        type = nat,
                        help = '''

                        exit after reporting N (10) lines that fail

                        ''')
    parser.add_argument('--no-limit', action = 'store_true',
                        dest = 'no_limit',
                        help = '''

                        report every line that fails, overriding
                        --limit

                        ''')

    args = parser.parse_args()
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):
    '''Transput HRT input stream in ins to TSV report in ous.

    '''

    setup_text(ous)

    occurrences = 0
    for k, line in enumerate(ins, start = 1):
        hits = re.findall('\xAD', line)
        if not hits: continue

        for hit in hits:
            occurrences += 1
            warn(k, 'code', 'U+{:04X} SOFT HYPHEN'.format(ord(hit)))

        if occurrences >= args.limit and not args.no_limit:
            warn(0, 'code',
                 'stopped checking at {}'.format(args.limit))
            return

    if args.info and not occurrences:
        info(0, 'code', 'no occurrences of SOFT HYPHEN')
