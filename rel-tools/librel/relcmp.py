# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-cmp,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

import sys

from .args import version_args
from .args import BadData
from .names import makenames
from .data import readhead, getter, records

def parsearguments(argv, *, prog = None):
    description = '''

    Compare two relations. Indicate the desired relationship by exit
    status.

    '''

    parser = version_args(description = description)

    parser.add_argument('inf1', 
                        help = '''

                        first relation

                        ''')

    parser.add_argument('inf2', nargs = '?',
                        help = '''

                        second relation (default stdin)

                        ''')

    group = parser.add_mutually_exclusive_group()
    
    group.add_argument('--quiet', '-q', action = 'store_true',
                        help = '''

                        suppress messages

                        ''')

    group.add_argument('--verbose', '-v', action = 'store_true',
                       help = '''

                       report how many records are only in first
                       relation, in both, and only in second (if
                       types are same)

                       ''')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('--eq', action = 'store_true',
                       help = '''

                       (equal) set status to 0 for equality, to 100
                       for inequality but the same type, to 123 for
                       different types

                       ''')

    group.add_argument('--ne', action = 'store_true',
                       help = '''

                       (not equal) set status to 0 for inequality,
                       including different types, to 100 for equality

                       ''')

    group.add_argument('--le', action = 'store_true',
                       help = '''

                       (less than or equal) set status to 0 if first
                       relation is a subset of the second relation,
                       to 100 if not but the types are same, to 123
                       for different types

                       ''')

    group.add_argument('--lt', action = 'store_true',
                       help = '''

                       (less than) set status to 0 if first relation
                       is a strict subset of the second relation, to
                       100 if not but the types are same, to 123 for
                       different types

                       ''')

    group.add_argument('--gt', action = 'store_true',
                       help = '''

                       (greater than) set status to 0 if first
                       relation is a strict superset of the second
                       relation, to 100 if not but the types are
                       same, to 123 for different types

                       ''')

    group.add_argument('--ge', action = 'store_true',
                       help = '''

                       (greather than or equal) set status to 0 if
                       first relation is a superset of the second
                       relation, to 100 if not but the types are
                       same, to 123 for different types

                       ''')
    
    group.add_argument('--cmp', '-c', action = 'store_true',
                       help = '''

                       (default) set status to 0 for equality, to 100
                       for imcomparability but the same type, to 101
                       if for a strict subset, to 102 for a strict
                       superset, to 123 for different types

                       ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args):

    status = 200 # this cannot happen
    try:
        with open(args.inf1, 'rb').detach() as ins1, \
             (
                 sys.stdin.buffer
                 if args.inf2 is None else
                 open(args.inf2, 'rb')

             ).detach() as ins2:

            status = compare(args, ins1, ins2)
    except Exception as exn:
        # the return in the finally takes over
        print(exn, file = sys.stderr)
    finally:
        return status

def compare(args, ins1, ins2):
    '''Print an appropriate message and return the appropriate status.

    Does the appropriate message belong in stdout or in stderr?

    '''

    def message(mess):
        if args.quiet: return
        out = (sys.stdout if args.verbose else sys.stderr)
        print('{}: {}'.format(args.prog, mess), file = out)
        return

    head1 = readhead(ins1)
    head2 = readhead(ins2)

    if not set(head1) == set(head2):
        if args.ne: return 0
        message('types differ')
        return 123

    ind1 = tuple(map(head1.index, head1))
    ind2 = tuple(map(head2.index, head1))
    
    # records() produces lists (because .split())
    # a getter produces tuples
    # lists and tuples are not comparable
    # which is awkward so use a getter even on body1
    get1 = getter(ind1)
    get2 = getter(ind2)

    both = only1 = only2 = 0
    try:
        body1 = map(get1, records(ins1, head = head1, key = ind1))
        body2 = map(get2, records(ins2, head = head2, key = ind2))
        r1 = next(body1, None)
        r2 = next(body2, None)
        while r1 is not None is not r2:
            if r1 == r2:
                both += 1
                r1 = next(body1, None)
                r2 = next(body2, None)
            elif r1 < r2:
                only1 += 1
                r1 = next(body1, None)
            else:
                only2 += 1
                r2 = next(body2, None)
        else:
            only1 += (r1 is not None) + sum(1 for r1 in body1)
            only2 += (r2 is not None) + sum(1 for r2 in body2)
    except Exception:
        raise

    if args.verbose:
        print('{}: only in first:'.format(args.prog), only1, sep = '\t')
        print('{}: in both:'.format(args.prog), both, sep = '\t')
        print('{}: only in second:'.format(args.prog), only2, sep = '\t')

    if args.eq:
        ( args.verbose and
          (only1 == only2 == 0) and message('relations are equal') )
        (only1 == only2 == 0) or message('bodies differ')
        return (0 if only1 == only2 == 0 else 100)

    if args.ne:
        ( args.verbose and
          ( (only1 == only2 == 0) or message('bodies differ') ) )
        (only1 == only2 == 0) and message('relations are equal')
        return (100 if only1 == only2 == 0 else 0)
    
    if args.le:
        ( args.verbose and
          (only1 == 0) and message('first is subset') )          
        (only1 > 0 < only2) and message('bodies are incomparable')
        (only1 > only2 == 0) and message('first is strict superset')
        return (0 if only1 == 0 else 100)

    if args.lt:
        ( args.verbose and
          (only1 == 0 < only2) and message('first is strict subset') )
        (only1 > 0 < only2) and message('bodies are incomparable')
        (only1 == only2 == 0) and message('relations are equal')
        (only1 > only2 == 0) and message('first is strict superset')
        return (0 if only1 == 0 < only2 else 100)

    if args.gt:
        ( args.verbose and
          (only1 > 0 == only2) and message('first is strict superset') )
        (only1 > 0 < only2) and message('bodies are incomparable')
        (only1 == only2 == 0) and message('relations are equal')
        (only1 == 0 < only2) and message('first is strict subset')
        return (0 if only1 > 0 == only2 else 100)

    if args.ge:
        ( args.verbose and
          (only2 == 0) and message('first is superset') )
        (only1 > 0 < only2) and message('bodies are incomparable')
        (only1 == 0 < only2) and message('first is strict subset')
        return (0 if only2 == 0 else 100)

    # default or explicit args.cmp

    if only1 == only2 == 0:
        args.verbose and message('relations are equal')
        return 0

    if only1 > 0 < only2:
        message('bodies are incomparable')
        return 100

    if only1 == 0:
        message('first is strict subset')
        return 101

    # only2 == 0
    message('first is strict superset')
    return 102
