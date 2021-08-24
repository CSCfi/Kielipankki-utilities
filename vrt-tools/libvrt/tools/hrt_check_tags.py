# -*- mode: Python; -*-

'''Implementation of hrt-check-tags.

https://en.wikipedia.org/wiki/Tags_(Unicode_block)

'''

from libvrt.args import BadData, nat
from libvrt.args import transput_args
from libvrt.check import setup_text
from libvrt.check import error, warn, info

import re

def parsearguments(argv, *, prog = None):

    description = '''

    Report on the use of Unicode tags, which used to be deprecated as
    "language tags", then no longer deprecated, and are now repurposed
    as emoji modifiers for regional flags in specific sequences.

    With --info, also include U+1F3F4, the flag that the tags should
    modify.


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

    # The characters themselves are valid in a regex range. The block
    # mirrors ASCII, with codes U+0000-U+001F reserved but unused with
    # the exception of U+0001 that is still deprecated. The reports
    # could be made more informative, but how likely does anyone even
    # attempt the currently correct use of these codes? Will be seen.
    # (Turns out the first examples found were correct!)

    FLAG = '\U0001F3F4'
    TAGS = ( '[{}\U000E0000-\U000E007F]'
             .format(FLAG if args.info else '')
             # FLAG is actually not a "tag" at all,
             # but tags are intended to modify FLAG
    )

    failures = 0
    for k, line in enumerate(ins, start = 1):
        hits = re.findall(TAGS, line)
        if not hits: continue

        for hit in hits:
            if hit == FLAG:
                # FLAG can be a hit only when args.info;
                # flags *should* follow FLAG,
                # ending with U+E007F.
                info(k, 'code', 'U+{:X} WAVING BLACK FLAG'
                     .format(ord(hit)))
                continue
            warn(k, 'code', 'tag U+{:X} ({})'
                 .format(ord(hit), ascii[hit]))

        failures += 1
        if failures >= args.limit and not args.no_limit:
            error(0, 'code',
                  'stopped checking at {}'.format(args.limit))
            return

    if args.info and not failures:
        info(0, 'code', 'no Unicode "tag" codes')

ascii = {
    '\U000E0000' : '^@',
    '\U000E0001' : '^A',
    '\U000E0002' : '^B',
    '\U000E0003' : '^C',
    '\U000E0004' : '^D',
    '\U000E0005' : '^E',
    '\U000E0006' : '^F',
    '\U000E0007' : '^G',
    '\U000E0008' : '^H',
    '\U000E0009' : '^I',
    '\U000E000A' : '^J',
    '\U000E000B' : '^K',
    '\U000E000C' : '^L',
    '\U000E000D' : '^M',
    '\U000E000E' : '^N',
    '\U000E000F' : '^O',
    '\U000E0010' : '^P',
    '\U000E0011' : '^Q',
    '\U000E0012' : '^R',
    '\U000E0013' : '^S',
    '\U000E0014' : '^T',
    '\U000E0015' : '^U',
    '\U000E0016' : '^V',
    '\U000E0017' : '^W',
    '\U000E0018' : '^X',
    '\U000E0019' : '^Y',
    '\U000E001A' : '^Z',
    '\U000E001B' : '^[',
    '\U000E001C' : '^\\',
    '\U000E001D' : '^]',
    '\U000E001E' : '^^',
    '\U000E001F' : '^_',
    '\U000E0020' : ' ',
    '\U000E0021' : '!',
    '\U000E0022' : '"',
    '\U000E0023' : '#',
    '\U000E0024' : '$',
    '\U000E0025' : '%',
    '\U000E0026' : '&',
    '\U000E0027' : "'",
    '\U000E0028' : '(',
    '\U000E0029' : ')',
    '\U000E002A' : '*',
    '\U000E002B' : '+',
    '\U000E002C' : ',',
    '\U000E002D' : '-',
    '\U000E002E' : '.',
    '\U000E002F' : '/',
    '\U000E0030' : '0',
    '\U000E0031' : '1',
    '\U000E0032' : '2',
    '\U000E0033' : '3',
    '\U000E0034' : '4',
    '\U000E0035' : '5',
    '\U000E0036' : '6',
    '\U000E0037' : '7',
    '\U000E0038' : '8',
    '\U000E0039' : '9',
    '\U000E003A' : ':',
    '\U000E003B' : ';',
    '\U000E003C' : '<',
    '\U000E003D' : '=',
    '\U000E003E' : '>',
    '\U000E003F' : '?',
    '\U000E0040' : '@',
    '\U000E0041' : 'A',
    '\U000E0042' : 'B',
    '\U000E0043' : 'C',
    '\U000E0044' : 'D',
    '\U000E0045' : 'E',
    '\U000E0046' : 'F',
    '\U000E0047' : 'G',
    '\U000E0048' : 'H',
    '\U000E0049' : 'I',
    '\U000E004A' : 'J',
    '\U000E004B' : 'K',
    '\U000E004C' : 'L',
    '\U000E004D' : 'M',
    '\U000E004E' : 'N',
    '\U000E004F' : 'O',
    '\U000E0050' : 'P',
    '\U000E0051' : 'Q',
    '\U000E0052' : 'R',
    '\U000E0053' : 'S',
    '\U000E0054' : 'T',
    '\U000E0055' : 'U',
    '\U000E0056' : 'V',
    '\U000E0057' : 'W',
    '\U000E0058' : 'X',
    '\U000E0059' : 'Y',
    '\U000E005A' : 'Z',
    '\U000E005B' : '[',
    '\U000E005C' : '\\',
    '\U000E005D' : ']',
    '\U000E005E' : '^',
    '\U000E005F' : '_',
    '\U000E0060' : '`',
    '\U000E0061' : 'a',
    '\U000E0062' : 'b',
    '\U000E0063' : 'c',
    '\U000E0064' : 'd',
    '\U000E0065' : 'e',
    '\U000E0066' : 'f',
    '\U000E0067' : 'g',
    '\U000E0068' : 'h',
    '\U000E0069' : 'i',
    '\U000E006A' : 'j',
    '\U000E006B' : 'k',
    '\U000E006C' : 'l',
    '\U000E006D' : 'm',
    '\U000E006E' : 'n',
    '\U000E006F' : 'o',
    '\U000E0070' : 'p',
    '\U000E0071' : 'q',
    '\U000E0072' : 'r',
    '\U000E0073' : 's',
    '\U000E0074' : 't',
    '\U000E0075' : 'u',
    '\U000E0076' : 'v',
    '\U000E0077' : 'w',
    '\U000E0078' : 'x',
    '\U000E0079' : 'y',
    '\U000E007A' : 'z',
    '\U000E007B' : '{',
    '\U000E007C' : '|',
    '\U000E007D' : '}',
    '\U000E007E' : '~',
    '\U000E007F' : '^?',
}
