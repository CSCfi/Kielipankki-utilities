# -*- mode: Python; -*-

'''Implementation of vrt-element-as-line, layer out of the token of a
specified type of element on a line.

'''

from argparse import ArgumentTypeError
from itertools import chain, filterfalse, takewhile
from operator import itemgetter
import re

from libvrt.args import BadData
from libvrt.args import transput_args

from libvrt.metaname import nametype # need checked

from libvrt.nameargs import bagtype, parsenames
from libvrt.nameline import isnameline, parsenameline

def character(arg):
    if len(arg) == 1:
        return arg.encode('UTF-8')
    raise ArgumentTypeError('not a character')

def parsearguments(argv, *, prog = None):

    description = '''

    Lay out each instance of the specified type of element as a line
    containing the tokens inside the element. Default is to lay out
    sentences so, selecting just the word field from each token.

    '''

    parser = transput_args(description = description,
                           inplace = False)

    parser.add_argument('--element', metavar = 'name',
                        type = nametype,
                        default = b'sentence',
                        help = '''

                        name of the element to lay out ("sentence")

                        ''')

    parser.add_argument('--field', '-f', metavar = 'name,*',
                        type = bagtype,
                        dest = 'fields', action = 'append',
                        default = [],
                        help = '''

                        names of the fields to extract for each token,
                        separated by commas or spaces, or repeat the
                        option ("word")

                        ''')

    parser.add_argument('--between', '-B', metavar = 'character',
                        type = character,
                        default = b' ',
                        help = '''

                        token separator (between tokens) (SPC)

                        ''')

    parser.add_argument('--within', '-W', metavar = 'character',
                        type = character,
                        default = b' ',
                        help = '''

                        field separator (within token) (SPC)

                        ''')

    args = parser.parse_args()
    args.prog = prog or parser.prog

    return args

def getget(wanted, found):
    index = [found.index(name) for name in wanted]
    if len(index) == 0:
        # this cannot happen in vrt-element-as-line: wanted simply
        # cannot be empty; but can happen in other tools, and this
        # function really wants to be in a library
        return lambda r: ()
    elif len(index) == 1:
        getone = itemgetter(*index)
        return lambda r: (getone(r),)
    else:
        return itemgetter(*index)

def main(args, ins, ous):
    '''Transput VRT (bytes) in ins to VRT (bytes) in ous.'''

    begin = (b''.join((b'<', args.element, b'>')),
             b''.join((b'<', args.element, b' ')))

    def not_end(line, *, end = b''.join((b'</', args.element, b'>'))):
        return not line.startswith(end)

    def build_token(line):
        record = line.rstrip(b'\r\n').split(b'\t')
        return args.within.join((
            value
            .replace(b'&lt;', b'<')
            .replace(b'&gt;', b'>')
            .replace(b'&amp;', b'&') # must be last
            for value in GET(record) # GET is set below
        ))

    wants = parsenames(args.fields) or [b'word']

    # collecting all lines (should not be too many) up to positional
    # attributes (inclusive), to find the field names; the lines are
    # then also chained to the rest of ins for actual processing.
    head = list(find_names(filterfalse(bytes.isspace, ins)))
    names = parsenameline(head[-1], required = wants)
    GET = getget(wants, names)

    while True:
        line = next(filterfalse(bytes.isspace, ins), None)
        if line is None: break
        if line.startswith(begin):
            tokens = (
                build_token(line)
                for line in takewhile(not_end, chain(head, ins))
                if not line.startswith(b'<')
            )
            ous.write(args.between.join(tokens))
            ous.write(b'\n')

def find_names(ins):
    '''Yield lines from the input stream up to and including the first
    occurrence of positional attributes.

    '''

    for line in filterfalse(bytes.isspace, ins):
        yield line
        if isnameline(line): return
        if not line.startswith(b'<'):
            raise BadData('no names before data')

    raise BadData('no names (nor data)')
