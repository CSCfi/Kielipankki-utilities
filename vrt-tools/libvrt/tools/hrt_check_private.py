# -*- mode: Python; -*-

'''Implementation of hrt-check-private.

https://en.wikipedia.org/wiki/Private_Use_Areas

'''

from libvrt.args import BadData, nat
from libvrt.args import transput_args
from libvrt.check import setup_text
from libvrt.check import error, warn, info

import re

def parsearguments(argv, *, prog = None):

    description = '''

    Report on private-use characters (BMP PUA; almost all of PUA-A,
    PUA-B; in Unicode category Co) in an "HRT" document lines
    (regardless of the HRT structure).

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

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):
    '''Transput HRT input stream in ins to TSV report in ous.

    '''

    setup_text(ous)

    # the characters themselves are valid in a regex range; the last
    # two code points in a plane are "non-characters" and excluded
    # from the supplementary PUA-A and PUA-B "private" ranges.

    PRIVATES = ''.join(('[',
                        '\ue000-\uF8FF',         # BMP PUA
                        '\U000F0000-\U000FFFFD', # PUA-A
                        '\U00100000-\U0010FFFD', # PUA-B
                        ']'))

    failures = 0
    for k, line in enumerate(ins, start = 1):
        hits = re.findall(PRIVATES, line)
        if not hits: continue

        for hit in hits:
            error(k, 'code', 'private U+{:X}'.format(ord(hit)))

        failures += 1
        if failures >= args.limit and not args.no_limit:
            error(0, 'code',
                  'stopped checking at {}'.format(args.limit))
            return

    if args.info and not failures:
        info(0, 'code', 'no private (BMP PUA; PUA-A, PUA-B) codes')
