# -*- mode: Python; -*-

'''Test pr1.

'''

from itertools import groupby
from subprocess import Popen, PIPE
import sys

from libvrt.args import transput_args
from libvrt.bad import BadData, BadCode
from libvrt.pr1 import transput

def _name(arg): return arg.encode('UTF-8')

def parsearguments(argv):
    description = '''

    Test protocol 1 aka pr1 of libvrt by using `cut -c -3` to add,
    after a named field, the first three characters from that field.
    The output field name is formed by appending "_ch3" to the input
    field name. (The test is only valid for ASCII input as long as
    `cut` only works correctly with ASCII characters.)

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
                        to all sentences), mark tokens in other
                        sentences (in some other class, or not in a
                        class) with an underscore

                        ''')

    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    proc = Popen([ 'cut', '-c', '-3' ],
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

    if args.word + b'_ch3' in old:
        raise BadData('already such field: {}_ch3'
                      .format(args.word.decode('UTF-8')))

    WORD = old.index(args.word)

    new = old[:]
    new.insert(WORD + 1, args.word + b'_ch3')
    return new

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
    '''Write the sentence (an iterator of token records) to the external
    process in the desired format (in this case, just each "word" on
    their own lines, followed by an empty line).

    '''
    for record in sentence:
        # should unescape the word
        proc.stdin.write(record[WORD])
        proc.stdin.write(b'\n')
    else:
        proc.stdin.write(b'\n')

def pr1_read(ins):
    '''Return a reader of sentences (iterators of token records) from the
    external process, one sentence at a time (in this case, a sequence
    of non-empty lines, with empty lines between sentences).

    '''
    for kind, group in groupby(ins, bytes.isspace):
        if not kind:
            yield (
                ( line.rstrip(b'\r\n') ,)
                for line in group
            )

def pr1_join(old, new, ous):
    ous.write(b'\t'.join((*old[:WORD + 1],
                          # should escape new
                          *new,
                          *old[WORD + 1:])))
    ous.write(b'\n')

def pr1_keep(old, ous):
    ous.write(b'\t'.join((*old[:WORD + 1],
                          b'_',
                          *old[WORD + 1:])))
    ous.write(b'\n')
