#! /usr/bin/env python3
# -*- mode: Python; -*-

'''A preliminary sentence polarity classifier, using pr1 and a meta
component. The underlying tool is written / trained on Suomi24 data /
installed in Puhti by Sam Hardwick.

'''

from argparse import ArgumentTypeError
from itertools import chain, groupby
from subprocess import Popen, PIPE
import re, sys

from libvrt.args import transput_args
from libvrt.bad import BadData, BadCode
from libvrt.pr1 import transput

def _name(arg):
    if re.fullmatch('\w+', arg, re.ASCII):
        return arg.encode('UTF-8')
    raise ArgumentTypeError('bad name: ' + repr(arg))

def parsearguments(argv):
    description = '''

    Run a polarity classifier, trained on Suomi24 data, on sentences
    in VRT documents, to add (or overwrite) in each processed sentence
    a new polarity code attribute.

    '''
    parser = transput_args(description = description)

    parser.add_argument('--word', '-w', metavar = 'name',
                        default = 'word',
                        type = _name,
                        help = '''

                        input field name (defaults to "word")

                        ''')
    parser.add_argument('--polarity', metavar = 'name',
                        default = 'polarity',
                        type = _name,
                        help = '''

                        output attribute name ("polarity")

                        ''')
    parser.add_argument('--class', '-c', dest = 'todo',
                        choices = (
                            'one',
                            'two'
                        ),
                        help = '''

                        only process sentences in the given class
                        (sentence attribute like class="one", default
                        to all sentences), leave other sentences (in
                        some other class, or not in a class) as they
                        were [this option is a remnant from a test
                        program, to be removed or not to be removed]

                        ''')

    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    # pytorch/1.6 is the default pytorch module at the time, needed to
    # run Sam's tool, apparently incompatible with something in kieli
    # module at the time, so loaded the module just for the external
    # process; in 2025, pytorch/1.6 is gone, but default seems to
    # work, so load default version now
    proc = Popen([ '/bin/bash', '-c',
                   '''

                   module load pytorch
                   /projappl/clarin/s24-cnn-sentiment/sentiment-classification/main.py

                   ''' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = None)

    return transput(args, sys.modules[__name__], proc, ins, ous)

WORD = None # field index
ATTR = None # sentence attribute name
TODO = None

def pr1_init(args, old):
    '''Return new (same as old) names. Establish the context for the
    protocol (in this case, the field index WORD, attribute name ATTR,
    and not sure if TODO will remain in any form).

    '''
    global WORD
    global ATTR
    global TODO

    # with `-c one`, pr1_test selects <sentence class="one">
    TODO = args.todo and ' class="{}"'.format(args.todo).encode('UTF-8')

    if args.word not in old:
        raise BadData('no such field: {}'
                      .format(repr(args.word.decode('UTF-8'))))

    WORD = old.index(args.word)
    ATTR = args.polarity

    return old

class _state: now = True
def pr1_test(*, meta = (), tags = ()):
    '''Establish whether to send the next sentence to the external tool.

    '''
    if not TODO: return True
    for tag in tags:
        if tag.startswith(b'</'): _state.now = False
        else: _state.now = (TODO in tag)
    else:
        return _state.now

def pr1_send(sentence, proc):
    '''Ship and clear any currently tracked meta, then ship the (tokens
    of) the current sentence, all in the format expected by the
    underlying tool.

    '''
    for k, record in enumerate(sentence):
        k and proc.stdin.write(b' ')
        proc.stdin.write(record[WORD]
                         # librarify already
                         .replace(b'&lt;', b'<')
                         .replace(b'&gt;', b'>')
                         # & intentionally last
                         .replace(b'&amp;', b'&'))
    else:
        proc.stdin.write(b'\n')

def pr1_read(ins):
    '''Return a reader of sentences analyses (a polarity code) from the
    external process, one sentence at a time.

    '''
    for line in ins:
        code = line.rstrip(b'\r\n')
        yield code

def pr1_join_meta(old, new, ous):
    '''Write old sentence start-tag line with new (whatever pr1_read
    yielded as a meta component - here just the polarity code) added
    to the attributes.

    '''
    meta = dict(re.findall(br'(\S+)="(.*?)"', old))
    meta[ATTR] = new
    ous.write(b'<sentence')
    for k, v in sorted(meta.items()):
        ous.write(b' ')
        ous.write(k),
        ous.write(b'="')
        ous.write(v)
        ous.write(b'"')
    else:
        ous.write(b'>\n')

def pr1_keep(old, ous):
    '''Keep old token as it was - no new field even.'''
    ous.write(b'\t'.join(old))
    ous.write(b'\n')
