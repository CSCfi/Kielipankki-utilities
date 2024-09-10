#! /usr/bin/env python3
# -*- mode: Python; -*-

'''A preprocessor to prevent vrt-finnish-nertag from attempting
certain types of sentence that the underlying finnish-nertag
empirically cannot handle. If such a pattern is detected in the token
sequence, the string "finnish-nertag" is inserted in the set-valued
sentence attribute _skip.

Oops.

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

    Mark with _skip="|finnish-nertag|" such sentences whose token
    patterns finnish-nertag (at version 1.6) is, empirically, not
    expected to handle gracefully. Use before vrt-finnish-nertag.

    '''
    parser = transput_args(description = description)

    parser.add_argument('--word', '-w', metavar = 'name',
                        default = 'word',
                        type = nametype,
                        help = '''

                        input field name [word]

                        ''')

    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    # set WORD to word field index (or raise BadData)
    # expecting positional-attributes line near top
    # (do we not have this in some library already?)
    head = list(islice(ins, 100))
    for line in head:
        if not isnameline(line): continue
        WORD = (
            parsenameline(line, required = { args.word })
            .index(args.word)
        )
        break
    else:
        raise BadData('positional attribute names not found')

    for k, sentence in enumerate(sentence_elements(chain(head, ins), ous)):
        ship_sentence(list(sentence), WORD, ous)

def ship_sentence(lines, WORD, ous):
    '''Ship sentence start tag with _skip="|finnish-nertag|" if any
    relevant issue is detected in text, else ship tag as is. Ship
    remaining sentence lines as they are.

    '''

    start = lines[0]

    # extract sentence contents as space-delimited tokens in UTF-8 for
    # convenient pattern matching; ignore any meta lines, if any (and
    # there are always at least two such, of course)
    text = (
        b' '.join(chain([b''],
                        (
                            unescape(record(line)[WORD])
                            for line in lines
                            if not line.startswith(b'<')
                        ),
                        [b'']))
        .decode('UTF-8')
    )

    # TODO proper pattern detection remains to be implemented
    #
    skip = bool(
        re.search(' [A-ZÅÄÖ]', text)
    )

    if skip:
        name = element(start)
        attributes = mapping(start)
        if b'_skip' in attributes:
            if b'|finnish-nertag|' in attributes[b'_skip']:
                pass
            else:
                attributes[b'_skip'] += b'finnish-nertag|'
        else:
            attributes[b'_skip'] = b'|finnish-nertag|'
        start = starttag(name, attributes)

    ous.write(start)
    for k, line in enumerate(lines):
        if k == 0: continue
        ous.write(line)
