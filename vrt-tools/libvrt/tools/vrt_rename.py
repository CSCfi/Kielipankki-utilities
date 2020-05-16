# -*- mode: Python; -*-

'''Implement vrt-rename.'''

from itertools import filterfalse, islice

from libvrt.args import transput_args
from libvrt.nameargs import maptype, parsemaps
from libvrt.nameline import isnameline, parsenameline, rename, makenameline
from libvrt.bad import BadData

def parsearguments():
    description = '''

    Rename some positional attributes aka fields.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--map', '-m', metavar = 'old=new,*',
                        dest = 'mapping', action = 'append',
                        type = maptype, default = [],
                        help = '''

                        map each old name to the new name, separate by
                        commas or spaces, or repeat the option

                        ''')
    args = parser.parse_args()
    args.prog = parser.prog
    return args

def main(args, ins, ous):
    '''Expect to find an old name line somewhere in the first 100 lines,
    before first token line. Ship a new name line instead, then ship
    all but old name lines in what remains.

    '''

    mapping = parsemaps(args.mapping)
    content = filterfalse(bytes.isspace, ins)

    # expect name comment in early lines
    head = islice(content, 100)
    for line in head:
        if isnameline(line):
            names = parsenameline(line, required = mapping.keys())
            ous.write(makenameline(rename(names, mapping)))
            break
        elif line.startswith(b'<'):
            ous.write(line)
        else:
            raise BadData('fields found before field names')
    else:
        raise BadData('first 100 lines: no field names found')

    # broke out of head so found and shipped a name line
    for line in filterfalse(isnameline, head): ous.write(line)
    for line in filterfalse(isnameline, content): ous.write(line)

    return 0
