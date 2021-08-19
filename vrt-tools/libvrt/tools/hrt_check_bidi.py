# -*- mode: Python; -*-

'''Implementation of hrt-check-bidi.

https://en.wikipedia.org/wiki/Bidirectional_text

'''

from libvrt.args import BadData, nat
from libvrt.args import transput_args
from libvrt.check import setup_text
from libvrt.check import error, warn, info

import re

def parsearguments(args, *, prog = None):

    description = '''

    Report on the use of Unicode explicit bidirectional formatting
    codes. These need not (necessarily) be errors, but their
    interaction with tokenization may be interesting. Also, letters
    should usually arrange themselves in the intended direction even
    without these explicit formatting codes.

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

    # The characters themselves are valid in a regex range.
    BIDI = ''.join(('[', *sorted(bidicode.keys()), ']'))
    
    occurrences = 0
    for k, line in enumerate(ins, start = 1):
        hits = re.findall(BIDI, line)
        if not hits: continue

        for hit in hits:
            occurrences += 1
            warn(k, 'code', 'U+{:X} {}'
                 .format(ord(hit), bidicode[hit]))

        if occurrences >= args.limit and not args.no_limit:
            warn(0, 'code',
                 'stopped checking at {}'.format(args.limit))
            return

    if args.info and not occurrences:
        info(0, 'code', 'no explicit BiDi codes')

bidicode = {
    '\u016C' : 'ARABIC LETTER MARK (ALM)',
    '\u200E' : 'LEFT-TO-RIGHT MARK (LRM)',
    '\u200F' : 'RIGHT-TO-LEFT MARK (RLM)',
    '\u2066' : 'LEFT-TO-RIGHT ISOLATE (LRI)',
    '\u2067' : 'RIGHT-TO-LEFT ISOLATE (RLI)',
    '\u2068' : 'FIRST STRONG ISOLATE (FSI)',
    '\u2069' : 'POP DIRECTIONAL ISOLATE (PDI)',
    '\u202A' : 'LEFT-TO-RIGHT EMBEDDING (LRE)',
    '\u202B' : 'RIGHT-TO-LEFT EMBEDDING (RLE)',
    '\u202C' : 'POP DIRECTIONAL FORMATTING (PDF)',
    '\u202D' : 'LEFT-TO-RIGHT OVERRIDE (LRO)',
    '\u202E' : 'RIGHT-TO-LEFT OVERRIDE (RLO)',
}
