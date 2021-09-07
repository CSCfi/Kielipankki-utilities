#! /usr/bin/env python3
# -*- mode: Python; -*-

'''A language-recognition implementation, using pr1 and a meta
component. The underlying tool is the HeLI recognizer that reads each
sentence on a line of its own and writes a corresponding language code
on a line of its own:

https://zenodo.org/record/5052819#.YTeUAVtRVH4

'''

from argparse import ArgumentTypeError
from itertools import chain, groupby
from subprocess import Popen, PIPE
import re, sys

from libvrt.args import transput_args
from libvrt.bad import BadData, BadCode
from libvrt.pr1 import transput

try:
    from outsidelib import HeLI
except ImportError as exn:
    # So it will crash when actually trying to launch the underlying
    # tool and HeLI is not defined, but --help and --version
    # options will work!
    print('Import Error:', exn, file = sys.stderr)

def _name(arg):
    if re.fullmatch('\w+', arg, re.ASCII):
        return arg.encode('UTF-8')
    raise ArgumentTypeError('bad name: ' + repr(arg))

def parsearguments(argv):

    description = '''

    Exercise a language-identification mechanism for sentences in VRT
    documents to add (or overwrite) in each processed sentence a new
    language code attribute.

    '''
    parser = transput_args(description = description)

    parser.add_argument('--word', '-w', metavar = 'name',
                        default = 'word',
                        type = _name,
                        help = '''

                        input field name (defaults to "word")

                        ''')
    parser.add_argument('--lang', metavar = 'name',
                        default = 'lang',
                        type = _name,
                        help = '''

                        output attribute name (defaults to "lang")

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

    # should add -c to also receive a confidence score; without
    # input/output filenames HeLi should work stdin/stdout
    proc = Popen([ 'java', '-jar', HeLI ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = None)

    return transput(args, sys.modules[__name__], proc, ins, ous)

WORD = None # field index
LANG = None # sentence attribute name
TODO = None
META = dict(text = None, para = None, sent = None) # ship and clear at data

def pr1_init(args, old):
    '''Return new (same as old) names. Establish the context for the
    protocol (in this case, the field index WORD, attribute name LANG,
    and not sure if TODO will remain in any form).

    '''
    global WORD
    global LANG
    global TODO

    # with `-c one`, pr1_test selects <sentence class="one">
    TODO = args.todo and ' class="{}"'.format(args.todo).encode('UTF-8')

    if args.word not in old:
        raise BadData('no such field: {}'
                      .format(repr(args.word.decode('UTF-8'))))

    WORD = old.index(args.word)
    LANG = args.lang

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
        # in an ideal world should unescape the word,
        # but even &amp; is presumably quite rare,
        # let alone &lt; or &gt;
        k and proc.stdin.write(b' ')
        proc.stdin.write(record[WORD])
    else:
        proc.stdin.write(b'\n')

def pr1_read(ins):
    '''Return a reader of sentences analyses (a language code) from the
    external process, one sentence at a time.

    '''
    for line in ins:
        lang = line.rstrip(b'\r\n')
        yield lang

def pr1_join_meta(old, new, ous):
    '''Write old sentence start-tag line with new (whatever pr1_read
    yielded as a meta component - here just the language code) added
    to the attributes.

    '''
    meta = dict(re.findall(br'(\S+)="(.*?)"', old))
    meta[LANG] = new
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
