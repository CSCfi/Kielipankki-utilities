#! /usr/bin/env python3
# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-image,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

# (subprocess.run is new in Python 3.5)

import os
import subprocess
from tempfile import mkstemp

from .args import transput_args
from .data import getter, readhead, groups

def parsearguments(argv, *, prog = None):
    description = '''

    The other fields of the records that match at least one record in
    another relation on the values in the fields that have the same
    name.

    '''

    parser = transput_args(description = description, matching = True)

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins1, ins2, ous):

    head1 = readhead(ins1)
    head2 = readhead(ins2)

    key = tuple(name for name in head1 if name in head2)
    oth = tuple(name for name in head1 if name not in head2)

    other = getter(tuple(k for k, name in enumerate(head1)
                         if name not in key))

    fd, tmp = mkstemp(prefix = 'image-', suffix = '.tsv.tmp')
    os.close(fd)
    try:
        body1 = groups(ins1, head = head1, key = tuple(map(head1.index, key)))
        body2 = groups(ins2, head = head2, key = tuple(map(head2.index, key)))
        k1, g1 = next(body1, (None, None))
        k2, g2 = next(body2, (None, None))
        with open(tmp, 'wb') as out:
            while k1 is not None is not k2:
                if k1 == k2:
                    for r1 in g1:
                        out.write(b'\t'.join(other(r1)))
                        out.write(b'\n')
                    else:
                        k1, g1 = next(body1, (None, None))
                        k2, g2 = next(body2, (None, None))
                elif k1 < k2:
                    k1, g1 = next(body1, (None, None))
                else:
                    k2, g2 = next(body2, (None, None))
            else:
                # any reason to drain ins1 or ins2?
                pass
            
        ous.write(b'\t'.join(oth))
        ous.write(b'\n')
        ous.flush()
        subprocess.run([ 'sort', '--unique', tmp ],
                       env = dict(os.environ,
                                  LC_ALL = 'C'),
                       stdout = ous,
                       stderr = None)
    except Exception:
        raise
    finally:
        os.remove(tmp)

    return 0
