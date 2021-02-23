#! /usr/bin/env python3
# -*- mode: Python; -*-

'''An identity transputation using pr1 (with a trivial meta component)
for testing the stderr handling mechanism. The underlying tool writes
to stderr.

'''

import os
from subprocess import Popen, PIPE
import sys

from libvrt.args import transput_args
from libvrt.pr1 import transput

# find external tool relative to
HERE = os.path.dirname(__file__)

def parsearguments(argv):
    description = '''

    Exercise a stderr-reading mechanism, using `tests/tools/bin/amp`
    to write to stderr, which is then filtered.

    '''
    parser = transput_args(description = description)

    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    # The detail to notice is that stderr is directed to a pipe, to be
    # read by pr1_read_stderr.

    proc = Popen([ os.path.join(HERE, 'bin', 'amp') ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)

    return transput(args, sys.modules[__name__], proc, ins, ous)

def pr1_init(args, old):
    '''Return new names, same as old names. Vacuously establish the
    context for the protocol.

    '''

    return old

def pr1_test(*, meta = (), tags = ()):
    '''Vacuously return True to indicate that the next sentence should be
    sent out to the underlying tool.

    '''

    return True

def pr1_send(sentence, proc):
    '''Ship the fields of the each record in the current sentence as one
    line, separated by spaces. The line is then read back (as meta)
    and ignored by pr1_join_meta but copies go to stderr, to be
    filtered by pr1_read_stderr.

    '''

    proc.stdin.write(b' '.join(field
                               for record in sentence
                               for field in record))
    proc.stdin.write(b'\n')

def pr1_read(ins):
    '''Return a reader of sentences analyses, just one line each.

    '''
    return ins

def pr1_join_meta(old, new, ous):
    '''Write old sentence start-tag line as is, ignoring "new" (which is
    actually just the line that was sent to proc for the sentence).

    '''
    ous.write(old)

def pr1_keep(old, ous):
    '''Keep old token as it was - no new field even.'''
    ous.write(b'\t'.join(old))
    ous.write(b'\n')

def pr1_read_stderr(args, err):
    for k, line in enumerate(err, start = 1):
        sys.stderr.buffer.write(b'{pr1_read_stderr}\t')
        sys.stderr.buffer.write(str(k).encode('UTF-8'))
        sys.stderr.buffer.write(b'\t')
        sys.stderr.buffer.write(line)
