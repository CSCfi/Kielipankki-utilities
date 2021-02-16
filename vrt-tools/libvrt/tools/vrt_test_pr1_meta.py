# -*- mode: Python; -*-

'''Test implementation of pr1 with a meta component: each sentence
acquires a new attribute, data (the tokens) are kept as they were.

'''

from itertools import groupby
from subprocess import Popen, PIPE
import re, sys

from libvrt.args import transput_args
from libvrt.bad import BadData, BadCode
from libvrt.pr1 import transput

def _name(arg): return arg.encode('UTF-8')

def parsearguments(argv):
    description = '''

    Test protocol 1 aka pr1 (only meta component) of libvrt by using
    `cut -f 3` to add to each processed sentence a new attribute
    ans="unkN" where N is a counter (overwriting any previous ans for
    that sentence).

    '''
    parser = transput_args(description = description)

    parser.add_argument('--word', '-w', metavar = 'name',
                        default = 'word',
                        type = _name,
                        help = '''

                        input field name (defaults to "word")

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
                        were

                        ''')

    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    proc = Popen([ 'cut', '-f', '3' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = None)

    return transput(args, sys.modules[__name__], proc, ins, ous)

WORD = None
TODO = None

def pr1_init(args, old):
    '''Return new names. Establish the context for the protocol (in this
    case, just the field index WORD).

    '''
    global WORD
    global TODO

    # with `-c one`, pr1_test selects <sentence class="one">
    TODO = args.todo and ' class="{}"'.format(args.todo).encode('UTF-8')

    if args.word not in old:
        raise BadData('no such field: {}'
                      .format(repr(args.word.decode('UTF-8'))))

    WORD = old.index(args.word)
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

def pr1_send(sentence, proc, *, box = [0]):
    '''Write the sentence (an iterator of token records) to the external
    process in the desired format (in this case, just a tab-separated
    record containing two junk fields and an identifier followed by
    the tokens.

    '''
    box[0] += 1
    proc.stdin.write(b'foo\tbar\tunk')
    proc.stdin.write(str(box[0]).encode('UTF-8'))
    for record in sentence:
        # should unescape the word
        proc.stdin.write(b'\t')
        proc.stdin.write(record[WORD])
    else:
        proc.stdin.write(b'\n')

def pr1_read(ins):
    '''Return a reader of sentences analyses (just a classifying
    identifier) from the external process, one sentence at a time (in
    this case, a line containing the identifier).

    '''
    for line in ins:
        yield line.rstrip(b'\r\n')

def pr1_join_meta(old, new, ous):
    '''Write old sentence start-tag line with new (whatever pr1_read
    yielded as a meta component - here just an identifier) added to
    the attributes.

    '''
    meta = dict(re.findall(br'(\S+)="(.*?)"', old))
    meta[b'ans'] = new
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
