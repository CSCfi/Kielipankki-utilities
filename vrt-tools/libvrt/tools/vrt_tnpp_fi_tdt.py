# -*- mode: Python; -*-

'''Implementation of Finnish-TDT VRT parser, using the "pr1" machinery
with TNPP (Turku Neural Parser Pipeline).

'''

from argparse import ArgumentTypeError
from itertools import groupby
from subprocess import Popen, PIPE
import os, re, sys

from libvrt.args import transput_args
from libvrt.bad import BadData, BadCode
from libvrt.dataline import unescape, escape
from libvrt.pr1 import transput

try:
    from outsidelib import TURKUNPPDIR
    PYTHON = os.path.join(TURKUNPPDIR, 'venv-tnpp/bin/python3')
    TURKUNPP = os.path.join(TURKUNPPDIR, 'tnpp_parse.py')
    TURKUNPP_FI_TDT = os.path.join(TURKUNPPDIR, 'models_fi_tdt_dia/pipelines.yaml')
except ImportError as exn:
    # So it will crash when actually trying to launch the underlying
    # tool and TURKUNPPDIR is not defined, but --help and --version
    # options will work!
    print('Import Error:', exn, file = sys.stderr)
    # Mock values for testing during development
    PYTHON = 'python3'
    # print('IMA:', __file__)
    TURKUNPP = os.path.join(os.path.dirname(__file__), 'mock-ud-parse.py')
    TURKUNPP_FI_TDT = 'TODO'

def _name(arg):
    # librarify this already!
    if re.fullmatch('[A-Za-z_][A-Za-z0-9_]*', arg):
        return arg.encode('UTF-8')
    raise ArgumentTypeError('bad name: {}'.format(repr(arg)))

def _affix(arg):
    # librarify this already! (like _name but can be empty)
    if re.fullmatch('([A-Za-z_][A-Za-z0-9_]*)?', arg):
        return arg.encode('UTF-8')
    raise ArgumentTypeError('bad affix: {}'.format(repr(arg)))

def parsearguments(argv):
    description = '''

    Parse Finnish VRT: pass the word field in a VRT document through
    the TNPP parser using Finnish-TDT model, insert output fileds
    after the word. Input VRT must have positional attribute names.

    '''
    parser = transput_args(description = description)

    parser.add_argument('--word', metavar = 'name',
                        default = 'word',
                        type = _name,
                        help = '''

                        input FORM name ("word")

                        ''')

    # TODO output field names id, base, upos, xpos, feats, head,
    # deprel; and a prefix and a suffix!

    parser.add_argument('--prefix', metavar = 'x',
                        default = '',
                        type = _affix,
                        help = '''

                        prefix to each output field name (empty)

                        ''')

    parser.add_argument('--suffix', metavar = 'x',
                        default = '_ud2',
                        type = _affix,
                        help = '''

                        suffix to each out field name ("_ud2")

                        ''')

    parser.add_argument('--id', metavar = 'name',
                        dest = 'ref',
                        default = 'ref',
                        type = _name,
                        help = '''

                        ID name ("ref")

                        ''')

    parser.add_argument('--base', metavar = 'name',
                        default = 'lemma',
                        type = _name,
                        help = '''

                        BASE name ("lemma")

                        ''')

    parser.add_argument('--upos', metavar = 'name',
                        default = 'pos',
                        type = _name,
                        help = '''

                        UPOS name ("pos")

                        ''')

    parser.add_argument('--xpos', metavar = 'name',
                        default = 'xpos',
                        type = _name,
                        help = '''

                        XPOS name ("xpos")

                        ''')

    parser.add_argument('--feat', metavar = 'name',
                        default = 'msd',
                        type = _name,
                        help = '''

                        FEAT name ("msd")

                        ''')

    parser.add_argument('--head', metavar = 'name',
                        default = 'dephead',
                        type = _name,
                        help = '''

                        HEAD name ("dephead")

                        ''')

    parser.add_argument('--rel', metavar = 'name',
                        default = 'deprel',
                        type = _name,
                        help = '''

                        DEPREL name ("deprel")

                        ''')

    # TODO something about skipping sentences? maybe later

    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    # must find the components somewhere
    # mocking for now
    proc = Popen([ PYTHON, TURKUNPP,
                   '--conf', TURKUNPP_FI_TDT,
                   'parse_conllu' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = None)
    # TODO stderr = PIPE
    # - requires a handler implementation
    # - though does this tool even write there?

    return transput(args, sys.modules[__name__], proc, ins, ous)

WORD = None

def pr1_init(args, old):
    '''Return new names. Establish the context for the protocol (in this
    case, just the field index WORD).

    '''
    global WORD

    if args.word not in old:
        raise BadData('no such input field: {}'
                      .format(repr(args.word.decode('UTF-8'))))

    outnames = [ args.prefix + name + args.suffix
                 for name in (args.ref,
                              args.base, args.upos, args.xpos,
                              args.feat, args.head, args.rel) ]

    clashes = [ name for name in outnames if name in old ]
    if clashes:
        raise BadData('output field names already in use: {}: {}'
                      .format(b', '.join(clashes).decode('UTF-8'),
                              b', '.join(old).decode('UTF-8')))

    if len(outnames) > len(set(outnames)):
        raise BadData('duplicates in output field names: {}'
                      .format(b', '.join(outnames).decode('UTF-8')))

    WORD = old.index(args.word)
    new = old[:WORD + 1] + outnames + old[WORD + 1:]

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
        word = unescape(record[WORD])
        proc.stdin.write(b'\t'.join((str(k).encode('UTF-8'),
                                     word, b'_',
                                     b'_', b'_', b'_',
                                     b'_', b'_',
                                     b'_', b'_',)))
        proc.stdin.write(b'\n')
    else:
        proc.stdin.write(b'\n')

def pr1_read(ins):
    '''Return a reader of sentences (iterators of token records) from the
    external process, one sentence at a time (in this case, a sequence
    of non-empty lines, with empty lines between sentences).

    This reader produces (ref, base, upos, xpos, feats, head, rel) for
    each token, ignoring (echoed) form, deps, misc.

    '''
    for kind, group in groupby(ins, bytes.isspace):
        if not kind:
            yield (
                (ref, base, upos, xpos, feats, head, rel)
                for line in group
                for ref, form, base, upos, xpos, feats, head, rel, _, _
                in [ line.rstrip(b'\r\n').split(b'\t') ]
            )

def pr1_join(old, new, ous):
    '''Pass on the old token record, with new annotations inserted after
    the "word" field.

    '''
    ref, base, upos, xpos, feats, head, rel = new
    base = escape(base)
    # TODO something about feats format: UD to VRT
    ous.write(b'\t'.join((*old[:WORD + 1],
                          ref, base, upos, xpos, feats, head, rel,
                          *old[WORD + 1:])))
    ous.write(b'\n')

def pr1_keep(old, ous):
    '''Pass on the old token record with placeholder values for the new
    annotation fields.

    '''
    ous.write(b'\t'.join((*old[:WORD + 1],
                          b'_', b'_', b'_',
                          b'_', b'_', b'_',
                          b'_',
                          *old[WORD + 1:MSD + 1])))
    ous.write(b'\n')
