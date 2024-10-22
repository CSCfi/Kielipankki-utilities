#! /usr/bin/env python3
# -*- mode: Python; -*-

'''A language-identification implementation, using pr1 and a meta
component. The underlying tool is the HeLI 2.0 recognizer that reads
each sentence on a line of its own and writes a corresponding language
code on a line of its own, with -c also a confidence score. (Old 1.3
produced no tab and no confidence score if code was xxx, this 2.0 is
better and produces und and a score instead. Though does it always?)

https://doi.org/10.5281/zenodo.6077089

'''

from argparse import ArgumentTypeError
from itertools import chain, groupby
from subprocess import Popen, PIPE
import re, sys

from libvrt.args import transput_args
from libvrt.nameargs import nametype
from libvrt.bad import BadData, BadCode
from libvrt.pr1 import transput
from libvrt.dataline import unescape

try:
    # leaving HeLI_1_3 in outsidelib for puhti for now but do we ever
    # need to run it again?
    from outsidelib import HeLI_2_0 as HeLI
except ImportError as exn:
    # So it will crash when actually trying to launch the underlying
    # tool and HeLI is not defined, but --help and --version
    # options will work!
    print('Import Error:', exn, file = sys.stderr)

def parsearguments(argv):

    description = '''

    Exercise a language-identification mechanism (HeLI OTS 2.0) for
    sentences in VRT documents to add (or overwrite) in each processed
    sentence a language code attribute, with a confidence value in
    another attribute.

    '''
    parser = transput_args(description = description)

    parser.add_argument('--word', '-w', metavar = 'name',
                        default = 'word',
                        type = nametype,
                        help = '''

                        input field name (defaults to "word")

                        ''')
    parser.add_argument('--lang', metavar = 'name',
                        default = 'lang',
                        type = nametype,
                        help = '''

                        output attribute name (defaults to "lang")
                        (confidence score with suffix "_conf", so
                        default "lang_conf")

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

    # option -c is to also receive a confidence score; without without
    # input/output filenames HeLi should work stdin/stdout
    proc = Popen([ 'java', '-jar', HeLI, '-c' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = None)

    return transput(args, sys.modules[__name__], proc, ins, ous)

WORD = None # field index
LANG = None # sentence attribute name
CONF = None # sentence attribute name (LANG_conf)
TODO = None
META = dict(text = None, para = None, sent = None) # ship and clear at data

def pr1_init(args, old):
    '''Return new (same as old) names. Establish the context for the
    protocol (in this case, the field index WORD, attribute name LANG,
    the corresponding attribute CONF, and not sure if TODO will remain
    in any form).

    '''
    global WORD
    global LANG
    global CONF # LANG_conf
    global TODO

    # with `-c one`, pr1_test selects <sentence class="one">
    TODO = args.todo and ' class="{}"'.format(args.todo).encode('UTF-8')

    if args.word not in old:
        raise BadData('no such field: {}'
                      .format(repr(args.word.decode('UTF-8'))))

    WORD = old.index(args.word)
    LANG = args.lang
    CONF = args.lang + b'_conf'

    return old

class _state: now = True
def pr1_test(*, meta = (), tags = ()):
    '''Establish whether to send the next sentence to the external tool.
    Except mainly keep track of the current context, to be shipped and
    cleared when first shipping a sentence in that context. (Remnant
    of a design where the language recognizer would have received such
    context information. Maybe some day it might actually use it?)

    '''
    for line in chain(meta, tags):
        atts = b'\t'.join(re.findall(b'\S+=".*?"', line)) + b'\n'
        if atts: atts = b'\t' + atts
        if line.startswith((b'<text>', b'<text ')):
            META['text'] = b'text' + atts
            META['para'] = None
            META['sent'] = None
        elif line.startswith((b'<paragraph>', b'<paragraph ')):
            META['para'] = b'para' + atts
            META['sent'] = None
        elif line.startswith((b'<sentence>', b'<sentence ')):
            META['sent'] = b'sent' + atts

    if not TODO: return True
    for tag in tags:
        if tag.startswith(b'</'): _state.now = False
        else: _state.now = (TODO in tag)
    else:
        return _state.now

def pr1_send(sentence, proc, *, box = [0]):
    '''Ship (except do not ship any more) and clear any currently tracked
    meta, then ship the (tokens of) the current sentence, all in the
    format expected by the underlying tool.

    '''
    for level in ('text', 'para', 'sent'):
        if META[level] is not None:
            # proc.stdin.write(META[level])
            META[level] = None

    box[0] += 1
    # proc.stdin.write(b'data\t')
    # proc.stdin.write(str(box[0]).encode('UTF-8'))
    for k, record in enumerate(sentence):
        k and proc.stdin.write(b' ')
        proc.stdin.write(unescape(record[WORD]))
    else:
        proc.stdin.write(b'\n')

def pr1_read(ins):
    '''Return a reader of sentences analyses (a language code with a
    confidence score) from the external process, one sentence at a
    time. For language "xxx" there is no confidence score, so yield
    0.0 for that.

    '''
    for line in ins:
        lang, conf = ( line.rstrip(b'\r\n').split(b'\t')
                       if b'\t' in line
                       else (line.rstrip(b'\r\n'), b"0.0")
        )
        yield lang, conf

def pr1_join_meta(old, new, ous):
    '''Write old sentence start-tag line with new (whatever pr1_read
    yielded as a meta component - here just the language code and its
    confidence score) added to the attributes.

    '''
    meta = dict(re.findall(br'(\S+)="(.*?)"', old))
    meta[LANG], meta[CONF] = new
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
