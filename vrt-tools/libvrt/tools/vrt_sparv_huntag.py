# -*- mode: Python; -*-

'''New implementation of Swedish VRT pos-tagger, using the "pr1"
machinery, following pr1 test implementation and the old version of
vrt-sparv-huntag.

'''

from argparse import ArgumentTypeError
from itertools import groupby
from subprocess import Popen, PIPE
import re, sys

from libvrt.args import transput_args
from libvrt.bad import BadData, BadCode
from libvrt.pr1 import transput

try:
    from outsidelib import HUNPOSTAG, HUNPOSMODELS
except ImportError as exn:
    # So it will crash when actually trying to launch the underlying
    # tool and HUNPOSTAG is not defined, but --help and --version
    # options will work!
    print('Import Error:', exn, file = sys.stderr)

def _name(arg):
    # librarify this already!
    if re.fullmatch('[A-Za-z][A-Za-z0-9]*', arg):
        return arg.encode('UTF-8')
    raise ArgumentTypeError('bad name: {}'.format(repr(arg)))

def parsearguments(argv):
    description = '''

    Postag Swedish VRT: pass the word field in a VRT document through
    the tagger from SPARV (SUC model, compatible with Swemalt), insert
    pos and msd fields after word (msd produced by the underlying
    tagger, pos extracted from msd). Input VRT must have positional
    attribute names.

    '''
    parser = transput_args(description = description)

    parser.add_argument('--word', metavar = 'name',
                        default = 'word',
                        type = _name,
                        help = '''

                        input word field name ("word")

                        ''')
    parser.add_argument('--pos', metavar = 'name',
                        default = 'pos',
                        type = _name,
                        help = '''

                        output pos field name ("pos")

                        ''')

    parser.add_argument('--msd', metavar = 'name',
                        default = 'msd',
                        type = _name,
                        help = '''

                        output msd field name ("msd")

                        ''')

    # TODO something about skipping sentences? maybe later

    parser.add_argument('--err',
                        choices = [
                            'all',
                            'none'
                        ],
                        default = 'none',
                        help = '''

                        how much of the stderr stream from the
                        underlying tool to let pass ("none")

                        ''')

    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    # TODO probably add morph table
    proc = Popen([ HUNPOSTAG, HUNPOSMODELS['sparv'] ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = None)
    # TODO stderr = PIPE
    # - requires a handler implementation
    # - requires support in pr1.py (MUST!)

    return transput(args, sys.modules[__name__], proc, ins, ous)

WORD = None

def pr1_init(args, old):
    '''Return new names. Establish the context for the protocol (in this
    case, just the field index WORD).

    '''
    global WORD

    if args.word not in old:
        raise BadData('no such field: {}'
                      .format(repr(args.word.decode('UTF-8'))))

    if args.pos in old:
        raise BadData('field already in use: {}'
                      .format(args.pos.decode('UTF-8')))

    if args.msd in old:
        raise BadData('field already in use: {]'
                      .format(args.msd.decode('UTF-8')))

    WORD = old.index(args.word)

    new = old[:]
    new.insert(WORD + 1, args.msd)
    new.insert(WORD + 1, args.pos)
    return new

def pr1_test(*, meta = (), tags = ()):
    '''Establish whether to send the next sentence to the external tool.
    Current answer: yes. Future answer may depend on lang and _skip.

    '''

    return True

def pr1_send(sentence, proc):
    '''Write the sentence (an iterator of token records) to the external
    process in the desired format (in this case, each "word" on its
    own line, empty line after a sentence.

    '''
    for record in sentence:
        # unescape the word
        proc.stdin.write(record[WORD]
                         .replace(b'&lt;', b'<')
                         .replace(b'&gt;', b'>')
                         .replace(b'&amp;', b'&'))
        proc.stdin.write(b'\n')
    else:
        proc.stdin.write(b'\n')

def pr1_read(ins):
    '''Return a reader of sentences (iterators of token records) from the
    external process, one sentence at a time (in this case, a sequence
    of non-empty lines, with empty lines between sentences).

    This reader produces a tag for each token.

    '''
    for kind, group in groupby(ins, bytes.isspace):
        if not kind:
            yield (
                # word tab tag => tag
                tag
                for line in group
                # why is there a trailing tab anyway
                for word, tag, _ in [line.rstrip(b'\r\n').split(b'\t')]
            )

def pr1_join(old, new, ous):
    '''Pass on the old token record, with new pos and msd tags
    inserted. Extract pos from msd.

    '''
    pos, *_ = new.split(b'.', 1)
    ous.write(b'\t'.join((*old[:WORD + 1],
                          pos or b'_',
                          new or b'_',
                          *old[WORD + 1:])))
    ous.write(b'\n')

def pr1_keep(old, ous):
    '''Pass on the old token record with placeholder values for the new
    pos and msd fields.

    '''
    ous.write(b'\t'.join((*old[:WORD + 1],
                          b'_',
                          b'_',
                          *old[WORD + 1:])))
    ous.write(b'\n')

def pr1_read_stderr(args, err):
    for line in err:
        if args.err == 'none':
            pass
        elif args.err == 'all':
            sys.stderr.buffer.write(line)
        else:
            raise BadCode('this cannot happen')
