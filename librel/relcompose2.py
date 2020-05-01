# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-compose2,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

# (subprocess.run is new in Python 3.5)

import os
import subprocess
from tempfile import mkstemp

from .args import transput_args
from .data import getter, readhead, groups
from .cache import Cache
from .bins import SORT

def parsearguments(argv, *, prog = None):
    description = '''

    The other fields of the records that match on the values in the
    fields that have the same name. (For two relations only. Not sure
    yet how meaningful a multi-relation composite is, or exactly how
    it should be defined.)

    '''

    parser = transput_args(description = description, matching = True)

    parser.add_argument('--cache', metavar = 'limit',
                        type = int, # want non-negative
                        default = 10000,
                        help = '''

                        In-memory record cache limit (default 10000
                        records, any excess spills to a temp file).

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins1, ins2, ous):

    head1 = readhead(ins1)
    head2 = readhead(ins2)

    key = tuple(name for name in head1 if name in head2)
    oth1 = tuple(name for name in head1 if name not in head2)
    oth2 = tuple(name for name in head2 if name not in head1)
    
    other1 = getter(tuple(k for k, name in enumerate(head1)
                          if name not in key))
    other2 = getter(tuple(k for k, name in enumerate(head2)
                          if name not in key))

    cache1 = Cache(args.cache, head = head1)
    cache2 = Cache(args.cache, head = head2)

    fd, tmp = mkstemp(prefix = 'compose2-', suffix = '.tsv.tmp')
    os.close(fd)
    try:
        body1 = groups(ins1, head = head1, key = tuple(map(head1.index, key)))
        body2 = groups(ins2, head = head2, key = tuple(map(head2.index, key)))
        k1, g1 = next(body1, (None, None))
        k2, g2 = next(body2, (None, None))
        with open(tmp, 'wb') as out:
            while k1 is not None is not k2:
                if k1 == k2:
                    cache1.cache(g1)
                    cache2.cache(g2)
                    for r1 in cache1:
                        for r2 in cache2:
                            out.write(b'\t'.join(other1(r1)))
                            oth1 and oth2 and out.write(b'\t')
                            out.write(b'\t'.join(other2(r2)))
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

        ous.write(b'\t'.join(oth1))
        oth1 and oth2 and ous.write(b'\t')
        ous.write(b'\t'.join(oth2))
        ous.write(b'\n')
        ous.flush()
        subprocess.run([ SORT, '--unique', tmp ],
                       env = dict(os.environ,
                                  LC_ALL = 'C'),
                       stdout = ous,
                       stderr = None)
    except Exception:
        raise
    finally:
        os.remove(tmp)
        cache1.release()
        cache2.release()

    return 0
