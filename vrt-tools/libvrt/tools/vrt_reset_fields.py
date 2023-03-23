# -*- mode: Python; -*-

'''Replace specified fields with any of given values as or not as the
value of a specified class atribute of sentences. Something like that.

Initially used to wipe out morpho-syntactic analyses from sentences
identified as a different language than the morpho-syntactic model
(parsed with an inappropriate parser).

'''

from argparse import ArgumentTypeError
from itertools import chain
from re import search

from libvrt.args import transput_args
from libvrt.dataline import record
from libvrt.nameline import isnameline, parsenameline

def _bintags_(arg):
    '''arg type for a (positive) number of tags separated by spaces or
    commas (not sanity checking tags themselves, but ASCII letters and
    digits should be safe - initially intended to be language codes)

    '''
    it = [ tag.encode() for tag in arg.replace(',', ' ').split() ]
    if it: return it
    raise ArgumentTypeError()

def _binname_(arg):
    '''arg type for an attribute name (TODO should sanity check)

    '''
    return arg.encode() # TODO should sanity check as attribute name

def _binnames_(arg):
    '''arg type for a (positive) number of field names separated by spaces
    or commas (TODO really should sanity check these)

    '''
    return _bintags_(arg) # TODO really should sanity check as names

def _binval_(arg):
    '''arg type for whatever val (but still should sanity check)'''
    return arg.encode()

def parsearguments(argv):
    description = '''

    Replace the values of the specified fields with the specified
    string (defaulting to _) in sentence elements that do or do not
    belong to a specified class according to a specified attribute.

    Initially intended to remove morpho-syntactic annotations from
    sentences not marked as being in Finnish (lang="fin") but previously
    parsed with a parser intended for Finnish.

    '''

    parser = transput_args(description = description)

    target = parser.add_mutually_exclusive_group(required = True)
    target.add_argument('--oneof', metavar = 'class,...',
                        type = _bintags_,
                        help = '''

                        reset if the sentence class is one of these
                        (separate with spaces or commas)

                        ''')
    target.add_argument('--notin', metavar = 'class,...',
                        type = _bintags_,
                        help = '''

                        reset if the sentence class is not any of
                        these, even when the sentence does not have
                        the class attribute (separate with spaces or
                        commas)

                        ''')

    parser.add_argument('--attr', '-a', metavar = 'name',
                        type = _binname_,
                        required = True,
                        help = '''

                        sentence class attribute

                        ''')
    parser.add_argument('--fields', '-f', metavar = 'name,...',
                        type = _binnames_,
                        required = True,
                        help = '''

                        reset these inside the specified sentence
                        elements

                        ''')
    parser.add_argument('--empty', '-e', metavar = 'value',
                        type = _binval_,
                        default = b'_',
                        help = '''

                        replacement value [_]

                        ''')

    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    head = []
    for line in ins: # assuming no empty lines? is that safe?
        head.append(line)
        if isnameline(line):
            break
        if line.startswith(b'<'):
            continue
        raise BadData('data line before name line')

    names = parsenameline(head[-1], required = args.fields)
    index = tuple(names.index(name) for name in args.fields)

    SKIP = False
    for line in chain(head, ins):
        if line.startswith((b'<sentence ', b'<sentence>')):
            # observe the second kind of start tags because a sentence
            # with no attributes may belong to the intended class,
            # which happens when the class is specified negatively
            #
            SKIP = skipping(args, line)
            ous.write(line)
        elif line.startswith(b'</sentence>'):
            SKIP = True
            ous.write(line)
        elif SKIP or line.startswith(b'<'):
            ous.write(line)
        else:
            data = record(line)
            for k in index: data[k] = args.empty
            ous.write(b'\t'.join(data))
            ous.write(b'\n')

def skipping(args, sent):
    '''Establish from a sentence start tag whether the tokens in the
    sentence should be skipped (shipped as is) or their fields reset.

    '''
    kv = b' ' + args.attr + b'="(.*?)"'
    mo = search(kv, sent)
    if mo is None:
        return not args.notin

    val = mo.group(1)

    # assume one of args.oneof and args.notin is empty:
    # - if args.oneof is not empty, skip if val not in it
    # - if args.notin is not empty, skip if val in it
    return ((args.oneof and val not in args.oneof) or
            (args.notin and (val in args.notin)))
