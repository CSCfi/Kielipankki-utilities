# -*- mode: Python; -*-

'''Implementation of hrt-check-nonchar.

http://www.unicode.org/faq/private_use.html

(Yes, that FAQ describes noncharacters in addition to private-use
characters, and yes, it spells "noncharacter" without a hyphen.)

'''

from libvrt.args import BadData, nat
from libvrt.args import transput_args
from libvrt.check import setup_text
from libvrt.check import error, warn, info

import re

def parsearguments(argv, *, prog = None):

    description = '''

    Report on the 66 noncharacters. None of them should occur.

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

    # The characters themselves are valid in a regex range; the last
    # two code points in any plane are "noncharacters", and there is
    # also a contiguous block of 32 noncharacter in BMP.

    NONS = ''.join(('[',
                    '\uFDD0-\uFDEF',         # block of 32 in BMP
                    '\uFFFE\uFFFF',          # last two of BMP
                    *( '{}{}'.format(chr((plane << 16) + 0xFFFE),
                                     chr((plane << 16) + 0xFFFF))
                       for plane in range(1, 17)),
                    ']'))

    failures = 0
    for k, line in enumerate(ins, start = 1):
        hits = re.findall(NONS, line)
        if not hits: continue

        for hit in hits:
            error(k, 'code', 'noncharacter U+{:04X}'.format(ord(hit)))

        failures += 1
        if failures >= args.limit and not args.no_limit:
            error(0, 'code',
                  'stopped checking at {}'.format(args.limit))
            return

    if args.info and not failures:
        info(0, 'code', 'no noncharacters')
