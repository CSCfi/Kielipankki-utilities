# -*- mode: Python; -*-

'''New implementation of Swedish VRT parser, using the "pr1"
machinery, following pr1 test implementation and the old version of
vrt-sparv-swemalt.

'''

from argparse import ArgumentTypeError
from itertools import groupby
from subprocess import Popen, PIPE
import re, sys

from libvrt.args import transput_args
from libvrt.bad import BadData, BadCode
from libvrt.pr1 import transput

try:
    from outsidelib import MALTPARSER, SWEMALTDIR, SWEMALTMODEL
except ImportError as exn:
    # So it will crash when actually trying to launch the underlying
    # tool and MALTPARSER is not defined, but --help and --version
    # options will work!
    print('Import Error:', exn, file = sys.stderr)

def _name(arg):
    # librarify this already!
    if re.fullmatch('[A-Za-z][A-Za-z0-9]*', arg):
        return arg.encode('UTF-8')
    raise ArgumentTypeError('bad name: {}'.format(repr(arg)))

def parsearguments(argv):
    description = '''

    Parse Swedish VRT: pass the word and msd fields in a VRT document
    through the Swemalt parser from SPARV, insert ref field after word
    and head, rel fields after msd. Input VRT must have positional
    attribute names.

    '''
    parser = transput_args(description = description)

    parser.add_argument('--word', metavar = 'name',
                        default = 'word',
                        type = _name,
                        help = '''

                        input word field name ("word")

                        ''')
    parser.add_argument('--msd', metavar = 'name',
                        default = 'msd',
                        type = _name,
                        help = '''

                        input msd field name ("msd")

                        ''')
    parser.add_argument('--ref', metavar = 'name',
                        default = 'ref',
                        type = _name,
                        help = '''

                        output ref field name ("ref")

                        ''')
    parser.add_argument('--head', metavar = 'name',
                        default = 'dephead',
                        type = _name,
                        help = '''

                        output head field name ("dephead")

                        ''')
    parser.add_argument('--rel', metavar = 'name',
                        default = 'deprel',
                        type = _name,
                        help = '''

                        output rel field name ("reprel")

                        ''')

    # TODO something about skipping sentences? maybe later

    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    proc = Popen([ 'java', '-jar', MALTPARSER,
                   '-v', 'warn',
                   '-w', SWEMALTDIR,
                   '-c', SWEMALTMODEL ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = None)
    # TODO stderr = PIPE
    # - requires a handler implementation
    # - though does this tool even write there?

    return transput(args, sys.modules[__name__], proc, ins, ous)

WORD = None
MSD = None

def pr1_init(args, old):
    '''Return new names. Establish the context for the protocol (in this
    case, just the field index WORD).

    '''
    global WORD, MSD

    for name in (args.word, args.msd):
        if name not in old:
            raise BadData('no such field: {}'
                          .format(repr(name.decode('UTF-8'))))

    for name in (args.ref, args.head, args.rel):
        if name in old:
            raise BadData('field already in use: {}'
                          .format(name.decode('UTF-8')))

    WORD = old.index(args.word)
    MSD = old.index(args.msd)

    new = old[:]
    if WORD < MSD: # sigh
        new.insert(MSD + 1, args.rel)
        new.insert(MSD + 1, args.head)
        new.insert(WORD + 1, args.ref)
    else:        
        new.insert(WORD + 1, args.ref)
        new.insert(MSD + 1, args.rel)
        new.insert(MSD + 1, args.head)
    return new

def pr1_test(*, meta = (), tags = ()):
    '''Establish whether to send the next sentence to the external tool.
    Current answer: yes. Future answer may depend on lang and _skip.

    '''

    return True

def pr1_send(sentence, proc):
    '''Write the sentence (an iterator of token records) to the external
    process in the desired format (in this case each "word" on its own
    line with a running number, pos and msd from hunpos output but in
    a different form, empty line after a sentence). Is that right?

    '''
    for k, record in enumerate(sentence, start = 1):
        # unescape the word (should be librarified)
        word = ( record[WORD]
                 .replace(b'&lt;', b'<')
                 .replace(b'&gt;', b'>')
                 .replace(b'&amp;', b'&')
        )
        msd = record[MSD]
        pos, *rest = msd.split(b'.')
        # that is what old vrt-sparv-swemalt used to send,
        # apparently (id, form, base, pos, xpos, feats)
        proc.stdin.write(b'\t'.join((str(k).encode('UTF-8'),
                                     word,                         
                                     b'_',
                                     pos,
                                     pos,
                                     b'|'.join(rest) or b'_')))
        proc.stdin.write(b'\n')
    else:
        proc.stdin.write(b'\n')

def pr1_read(ins):
    '''Return a reader of sentences (iterators of token records) from the
    external process, one sentence at a time (in this case, a sequence
    of non-empty lines, with empty lines between sentences).

    This reader produces (ref, head, rel) for each token. The rest of
    the parser output is just echoed back by the parser (as is ref).

    '''
    for kind, group in groupby(ins, bytes.isspace):
        if not kind:
            yield (
                (ref, head, rel)
                for line in group
                for ref, form, base, pos, xpos, feats, head, rel
                in [ line.rstrip(b'\r\n').split(b'\t') ]
            )

def pr1_join(old, new, ous):
    '''Pass on the old token record, with new ref, head and rel values
    inserted.

    '''
    ref, head, rel = new
    ous.write(b'\t'.join((*old[:WORD + 1],
                          ref,
                          *old[WORD + 1:MSD + 1],
                          head,
                          rel,
                          *old[MSD + 1:])
                         if WORD < MSD else # sigh
                         (*old[:MSD + 1],
                          head,
                          rel,
                          *old[MSD + 1:WORD + 1],
                          ref,
                          *old[WORD + 1:])))
    ous.write(b'\n')

def pr1_keep(old, ous):
    '''Pass on the old token record with placeholder values for the new
    ref, head and rel fields.

    '''
    ous.write(b'\t'.join((*old[:WORD + 1],
                          b'_',
                          *old[WORD + 1:MSD + 1],
                          b'_',
                          b'_',
                          *old[MDS + 1:])
                         if WORD < MSD else # sigh
                         (*old[:MSD + 1],
                          b'_',
                          b'_',
                          *old[MSD + 1:WORD + 1],
                          b'_',
                          *old[WORD + 1:])))
    ous.write(b'\n')
