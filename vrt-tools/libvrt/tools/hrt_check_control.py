# -*- mode: Python; -*-

'''Implementation of hrt-check-control.'''

from libvrt.args import BadData, nat
from libvrt.args import transput_args
from libvrt.check import setup_text
from libvrt.check import error, warn, info

import re

def parsearguments(argv, *, prog = None):

    description = '''

    Report on unwanted control characters (Unicode C0, DEL, C1,
    Unicode category Cc) in an "HRT" document lines (regardless of the
    HRT structure). Also report on LS and PS (which are in their own
    Unicode categories Zl and Zp).

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

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):
    '''Transput HRT input stream in ins to TSV report in ous.

    '''

    setup_text(ous)

    # the characters themselves are valid in a regex
    CONTROLS = ''.join(('[', *sorted(tables), ']'))

    failures = 0
    for k, line in enumerate(ins, start = 1):
        hits = re.findall(CONTROLS, line)
        if not hits: continue

        for hit in hits:
            error(k, 'code', tables[hit])

        failures += 1
        if failures >= args.limit and not args.no_limit:
            return

    if args.info and not failures:
        info(0, 'code', 'no spurious control (C0, DEL, C1) codes')

tables = {
    # C0 and DEL adapted from Linux programmer's manual, ASCII(7)
    '\x00' : "U+0000 C0 NUL '\\0' (null character) ^@",
    '\x01' : "U+0001 C0 SOH (start of heading) ^A",
    '\x02' : "U+0002 C0 STX (start of text) ^B",
    '\x03' : "U+0003 C0 ETX (end of text) ^C",
    '\x04' : "U+0004 C0 EOT (end of transmission) ^D",
    '\x05' : "U+0005 C0 ENQ (enquiry) ^E",
    '\x06' : "U+0006 C0 ACK (acknowledge) ^F",
    '\x07' : "U+0007 C0 BEL '\\a' (bell) ^G",
    '\x08' : "U+0008 C0 BS '\\b' (backspace) ^H",
    # '\x09' : "U+0009 C0 HT '\\t' (horizontal tab) ^I",
    # '\x0A' : "U+000A C0 LF '\\n' (new line) ^J",
    '\x0B' : "U+000B C0 VT '\\v' (vertical tab) ^K",
    '\x0C' : "U+000C C0 FF '\\f' (form feed) ^L",
    '\x0D' : "U+000D C0 CR '\\r' (carriage return) ^M",
    '\x0E' : "U+000E C0 SO (shift out) ^N",
    '\x0F' : "U+000F C0 SI (shift in) ^O",
    '\x10' : "U+0010 C0 DLE (data link escape) ^P",
    '\x11' : "U+0011 C0 DC1 (device control 1) ^Q",
    '\x12' : "U+0012 C0 DC2 (device control 2) ^R",
    '\x13' : "U+0013 C0 DC3 (device control 3) ^S",
    '\x14' : "U+0014 C0 DC4 (device control 4) ^T",
    '\x15' : "U+0015 C0 NAK (negative acknowledge) ^U",
    '\x16' : "U+0016 C0 SYN (synchronous idle) ^V",
    '\x17' : "U+0017 C0 ETB (end of transmission blk) ^W",
    '\x18' : "U+0018 C0 CAN (cancel) ^X",
    '\x19' : "U+0019 C0 EM (end of medium) ^Y",
    '\x1A' : "U+001A C0 SUB (substitute) ^Z",
    '\x1B' : "U+001B C0 ESC (escape) ^[",
    '\x1C' : "U+001C C0 FS (file separator) ^\\",
    '\x1D' : "U+001D C0 GS (group separator) ^]",
    '\x1E' : "U+001E C0 RS (record separator) ^^",
    '\x1F' : "U+001F C0 US (unit separator) ^_",
    '\x7F' : "U+007F DEL",

    # C1 adapted from Wikipedia
    # https://en.wikipedia.org/wiki/Latin-1_Supplement_(Unicode_block)
    '\x80' : 'U+0080 C1 Padding Character (PAD)',
    '\x81' : 'U+0081 C1 High Octet Preset (HOP)',
    '\x82' : 'U+0082 C1 Break Permitted Here (BPH)',
    '\x83' : 'U+0083 C1 No Break Here (NBH)',
    '\x84' : 'U+0084 C1 Index (IND)',
    '\x85' : 'U+0085 C1 Next Line (NEL)',
    '\x86' : 'U+0086 C1 Start of Selected Area (SSA)',
    '\x87' : 'U+0087 C1 End of Selected Area (ESA)',
    '\x88' : 'U+0088 C1 Character (Horizontal) Tabulation Set (HTS)',
    '\x89' : 'U+0089 C1 Character (Horizontal) Tabulation with Justification (HTJ)',
    '\x8A' : 'U+008A C1 Line (Vertical) Tabulation Set (LTS)',
    '\x8B' : 'U+008B C1 Partial Line Forward (Down) (PLD)',
    '\x8C' : 'U+008C C1 Partial Line Backward (Up) (PLU)',
    '\x8D' : 'U+008D C1 Reverse Line Feed (Index) (RI)',
    '\x8E' : 'U+008E C1 Single-Shift Two (SS2)',
    '\x8F' : 'U+008F C1 Single-Shift Three (SS3)',
    '\x90' : 'U+0090 C1 Device Control String (DCS)',
    '\x91' : 'U+0091 C1 Private Use One (PU1)',
    '\x92' : 'U+0092 C1 Private Use Two (PU2)',
    '\x93' : 'U+0093 C1 Set Transmit State (STS)',
    '\x94' : 'U+0094 C1 Cancel character (CCH)',
    '\x95' : 'U+0095 C1 Message Waiting (MW)',
    '\x96' : 'U+0096 C1 Start of Protected Area (SPA)',
    '\x97' : 'U+0097 C1 End of Protected Area (EPA)',
    '\x98' : 'U+0098 C1 Start of String (SOS)',
    '\x99' : 'U+0099 C1 Single Graphic Character Introducer (SGCI)',
    '\x9A' : 'U+009A C1 Single Character Introducer (SCI)',
    '\x9B' : 'U+009B C1 Control Sequence Introducer (CSI)',
    '\x9C' : 'U+009C C1 String Terminator (ST)',
    '\x9D' : 'U+009D C1 Operating System Command (OSC)',
    '\x9E' : 'U+009E C1 Private Message (PM)',
    '\x9F' : 'U+009F C1 Application Program Command (APC) ',

    '\u2028' : 'U+2028 LINE SEPARATOR (LS, LSEP)',
    '\u2029' : 'U+2029 PARAGRAPH SEPARATOR (PS, PSEP)'
}
