# -*- mode: Python; -*-

'''Implement vrt-drop.

Warning! No longer expecting any name line to contain a '+', ever.
Develop a transparent mechanism for internal meta instead. Please.

'''

from itertools import chain, filterfalse, islice

from libvrt.args import transput_args
from libvrt.bad import BadData
from libvrt.keeper import keeper
from libvrt.nameargs import bagtype, parsenames
from libvrt.nameline import isnameline, parsenameline, makenameline

def parsearguments():
    description = '''

    Drop the named fields aka positional attributes.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--field', '-f', metavar = 'name,*',
                        dest = 'fields', default = [],
                        type = bagtype, action = 'append',
                        help = '''

                        fields to drop, separate names by commas or
                        spaces, or repeat the option

                        ''')

    parser.add_argument('--names', '-n', metavar = 'name,*',
                        dest = 'fields',
                        type = bagtype, action = 'append',
                        help = '(deprecated) use --field/-f instead')

    parser.add_argument('--dots', action = 'store_true',
                        help = '''

                        drop any fields with a dot in their name

                        ''')

    args = parser.parse_args()
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    # print(args.fields)
    drop = parsenames(args.fields)

    content = filterfalse(bytes.isspace, ins)

    head = islice(content, 100)
    for line in head:
        if isnameline(line):
            names = parsenameline(line, required = drop)
            ix = tuple(k for k, name in enumerate(names)
                       # *keep* the field if not -f name
                       # *and* *not* (--dots and dotted)
                       if name.rstrip(b'/') not in drop
                       if not (args.dots and (b'.' in name)))
            if len(ix) == 0:
                raise BadData('not allowed to drop all fields')
            keep = keeper(*ix)
            ous.write(makenameline(keep(names)))
            break
        elif line.startswith(b'<'):
            ous.write(line)
        else:
            raise BadData('fields found before field names')
    else:
        raise BadData('first 100 lines: no field names found')

    # broke out of head so found and shipped a name line
    for line in filterfalse(isnameline, chain(head, content)):
        if line.startswith(b'<'):
            ous.write(line)
            continue

        ous.write(b'\t'.join(keep(line.rstrip(b'\r\n').split(b'\t'))))
        ous.write(b'\n')

    return 0
