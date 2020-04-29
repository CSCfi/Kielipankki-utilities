#! /usr/bin/env python3
# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-join,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import os
from tempfile import mkstemp

from .args import transput_args
from .args import BadData
from .names import makenames
from .data import getter, readhead, groups
from .cache import Cache

def parsearguments(argv, *, prog = None):
    description = '''

    Join two or more relations on the values in the fields that have
    the same name.

    '''

    parser = transput_args(description = description, joining = True)

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins1, ins2, ous):

    # transput arranges to open two input streams, with the path names
    # to remaining input relations in args.rest (if any) and it seems
    # quite tricky to pass only the final result to the provided
    # stream while removing all temp files of temporary results:

    tmp1 = None
    try:
        for infk in args.rest:
            fd, tmp2 = mkstemp(prefix = 'join-', suffix = '.tsv.tmp')
            os.close(fd)
            with open(tmp2, 'wb') as ous2:
                join(ins1, ins2, ous2, many = 3)
            if tmp1 is not None:
                ins1.close()
                os.remove(tmp1)
            tmp1 = tmp2
            ins1 = open(tmp1, 'rb').detach() # magic
            ins2 = open(infk, 'rb').detach() # magic
        else:
            join(ins1, ins2, ous, many = 3)
    except Exception:
        raise
    finally:
        if tmp1 is not None:
            ins1.close()
            os.remove(tmp1)

    return 0

def join(ins1, ins2, ous, *, many):
    head1 = readhead(ins1)
    head2 = readhead(ins2)

    key = tuple(name for name in head1 if name in head2)
    oth = tuple(name for name in head2 if name not in head1)

    other = getter(tuple(k for k, name in enumerate(head2)
                         if name not in key))

    ous.write(b'\t'.join(head1))
    head1 and oth and ous.write(b'\t')
    ous.write(b'\t'.join(oth))
    ous.write(b'\n')

    cache1 = Cache(many)
    cache2 = Cache(many)

    try:
        body1 = groups(ins1, key = tuple(map(head1.index, key)))
        body2 = groups(ins2, key = tuple(map(head2.index, key)))
        k1, g1 = next(body1, (None, None))
        k2, g2 = next(body2, (None, None))
        while k1 is not None is not k2:
            if k1 == k2:
                cache1.cache(g1)
                cache2.cache(g2)
                for r1 in cache1:
                    for r2 in cache2:
                        ous.write(b'\t'.join(r1))
                        r1 and ous.write(b'\t')
                        ous.write(b'\t'.join(other(r2)))
                        ous.write(b'\n')
                k1, g1 = next(body1, (None, None))
                k2, g2 = next(body2, (None, None))
            elif k1 < k2:
                k1, g1 = next(body1, (None, None))
            else:
                k2, g2 = next(body2, (None, None))
        else:
            # any reason to drain ins1 or ins2?
            pass
    except Exception:
        raise
    finally:
        cache1.release()
        cache2.release()
