#! /usr/bin/env python3
# -*- mode: Python; -*-

'''A post-processor to 

'''

from argparse import ArgumentTypeError
from itertools import chain, islice # , groupby
import re, sys

from libvrt.args import transput_args
from libvrt.elements import sentence_elements
from libvrt.nameargs import nametype
from libvrt.nameline import isnameline, parsenameline
from libvrt.bad import BadData, BadCode
from libvrt.dataline import record, unescape
from libvrt.metaline import element, mapping, starttag

def parsearguments(argv):

    description = '''

    Split tokens within sentence elements if they appear to contain
    internal punctuation that should have been accompanied with a
    space but was not; possibly also insert a sentence boundary at
    that point.

    Token parts before the last are given all empty fields, indicated
    with | if the field name ends in /, else with _, as usual; a
    special field is set to SpaceAfter=no (multi-valued variant not
    implemented! TODO if needed). The last part carries the fields of
    the original mangled token.

    '''
    parser = transput_args(description = description)

    parser.add_argument('--word', '-w', metavar = 'name',
                        default = 'word',
                        type = nametype,
                        help = '''

                        input field name [word]

                        ''')

    parser.add_argument('--spaces', '-s', metavar = 'name',
                        default = 'spaces',
                        type = nametype,
                        help = '''

                        field for SpaceAfter=no, multi-valued if name
                        ends in / (not implemented!), else
                        single-valued [spaces] (set explicitly to the
                        empty string if no such field)

                        ''')

    parser.add_argument('--mark', action = 'store_true',
                        help = '''

                        impossibly prefix new tokens with "@>" and
                        have attribute _fix="@no-space" in new
                        sentence start tags for easy ocular inspection
                        of the changes; grep -C N is your friend

                        ''')

    parser.add_argument('--tag', action = 'store_true',
                        help = '''

                        tag new tokens and new sentence breaks with a
                        label to indicate what pattern produced them

                        ''')

    parser.add_argument('--wrap', action = 'store_true',
                        help = '''

                        impossibly wrap new tokens in "@<" and ">" for
                        another kind of easy ocular inspection of the
                        changes

                        ''')


    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    global WORD, TEMP, ARGS

    # set WORD to word field index (or raise BadData)
    # expecting positional-attributes line near top
    # (do we not have this in some library already?)
    head = list(islice(ins, 100))
    for line in head:
        if not isnameline(line): continue
        names = parsenameline(line, required = { args.word })
        WORD = names.index(args.word)
        TEMP = [
            (b'|' if name.endswith(b'/') else b'_')
            for name in names
        ]
        if args.spaces:
            if args.spaces not in names:
                raise BadData('not in names: ' + args.spaces.decode())
            # BUG TODO depend on whether there is / at end
            TEMP[names.index(args.spaces)] = b'SpaceAfter=no'
        break
    else:
        raise BadData('positional attribute names not found')

    ARGS = args

    for k, sentence in enumerate(sentence_elements(chain(head, ins), ous)):
        lines = list(sentence) # reify just in case?
        for line in lines:
            if line.startswith(b'<'):
                ous.write(line)
                continue
            if lower_dot_Cap(line, ous):
                continue
            ous.write(line)

# To fullmatch, first part matches all lowercase, second part matches
# a capitalized but otherwise lowercase word, separated by a single
# period; mostly this becomes a new sentence break, first part and
# period being new tokens in the first sentence and the second part
# replacing old token word in the second sentence. Do try to recognize
# some specific exceptions.
lower_dot_Cap_pattern = r'([a-zåäö]+[a-zåäö])[.]([A-ZÅÄÖ][a-zåäö]+)'

def lower_dot_Cap(line, ous):
    '''If the word in the line matches, ship the new lines and return
    True. Else return False.

    '''
    rec = record(line)
    # nothing to unescape in word if the pattern matches
    word = rec[WORD].decode()
    mo = re.fullmatch(lower_dot_Cap_pattern, word)
    if mo is None:
        return False
    part0, part2 = mo.groups()
    tag =  b'low.cap'
    for line in (
            # these will carry a grep-able tag if ARGS.mark
            new_line(part0.encode(), tag),
            new_line(b'.', tag),
            *new_break(tag),
            old_line(part2.encode(), rec, tag) ):
        ous.write(line)
    else:
        return True

def mark(word, tag):
    '''Return word with grep-able markup or tag or both if some of
    ARGS.mark or ARGS.tag or ARGS.wrap

    '''
    word = b'(' + tag + b')' + word if ARGS.tag else word
    word = b'@<' + word + b'>'  if ARGS.wrap else word
    word = b'@>' + word if ARGS.mark else word
    return word

def new_line(word, tag):
    '''Return a new token line for word, prefixed with tag if ARGS.mark,
    SpaceAfter=no for no space after if a spaces field is specified,
    and other fields suitably empty.

    '''
    rec = TEMP[:WORD] + [ mark(word, tag) ] + TEMP[WORD + 1:]
    return b'\t'.join(rec) + b'\n'

def old_line(word, rec, tag):
    '''Return a replacement for the old token line, word being the last
    part of an original word, prefixed with tag if ARGS.mark, and
    other fields whatever they were.

    '''
    # the program probably could get away with just modifying rec here
    # but that would be kind of horrible, so be kind and copy instead

    rec = rec[:WORD] + [ mark(word, tag) ] + rec[WORD + 1:]
    return b'\t'.join(rec) + b'\n'

def new_break(tag):
    '''Return a sentence end line and a sentence start line for a new line
    break. Include a _fix="@no-space" if ARGS.mark or ARGS.wrap,
    _fix="@no-space(tag)" if ARGS.tag the new start tag. (So there
    could actually be an option to produce just the attribute and
    leave tokens alone. But not all new breaks result in a sentence
    break at all. Also could have an option to not mark sentence tags
    while marking tokens. So many possibilities.)

    '''
    _fix = (
        b' _fix="@no-space(' + tag + b')"'
        if ARGS.tag else
        b' _fix="@no-space"'
        if ARGS.mark or ARGS.wrap else
        b''
    )
        
    return (
        b'</sentence>\n',
        b'<sentence' + _fix + b'>\n'
    )
