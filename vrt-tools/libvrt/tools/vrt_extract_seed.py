
"""
vrt_extract_seed.py

The actual implementation of vrt-extract-seed.

Please run "vrt-extract-seed -h" for more information.
"""


import random

from argparse import ArgumentTypeError

from vrtargsoolib import InputProcessor
from vrtnamelib import isbinnames, binnamelist, nameindex


def posint(arg):
    """Type check for `ArgumentParser`: `arg` must be a positive integer."""
    try:
        arg = int(arg)
        if arg > 0:
            return arg
    except ValueError:
        pass
    raise ArgumentTypeError('positive integer required')


# Values for args.distance with --distance="even", --distance="random"
DIST_EVEN = -1
DIST_RANDOM = -2


def distance_arg(arg):
    """`ArgumentParser` type check: `arg` is positive integer or ``even``. """
    try:
        return posint(arg)
    except ArgumentTypeError:
        if arg == 'even':
            return DIST_EVEN
        elif arg == 'random':
            return DIST_RANDOM
        else:
            raise ArgumentTypeError(
                'positive integer, "even" or "random" required')


class SeedExtractor(InputProcessor):

    """Class implementing vrt-extract-seed functionality."""

    DESCRIPTION = """
    Extract words (word forms) from VRT input for a random number
    generator seed.
    """
    ARGSPECS = [
        ('--count = num',
         '''the maximum number of words to extract for the seed''',
         dict(type=posint, default=100)),
        ('--distance = dist',
         '''the distance between the words to extract: positive
            integer, or "even" for evenly distributed or "random" for
            uniformly randomly distributed up to the token number
            specified with --last''',
         dict(type=distance_arg, default=100)),
        ('--last = num',
         '''the number of the last token to include in the seed
            (typically the number of tokens in the input VRT), to be
            used with --distance=even and --distance=random''',
         dict(type=posint)),
        ('--baseseed = str',
         '''use str as the random number generator seed for
            --distance=random (default: "" = non-reproducible
            output)''',
         dict(default='')),
        ('--separator = sep',
         '''separate words in output with sep''',
         dict(default='')),
    ]

    def __init__(self):
        super().__init__()

    def check_args(self, args):
        """Check the validity of `args` (combinations of options)."""
        if args.distance == DIST_EVEN and not args.last:
            self.error_exit('error: --distance=even requires specifying --last')
        elif args.distance == DIST_RANDOM:
            if not args.last:
                self.error_exit(
                    'error: --distance=random requires specifying --last')
            elif args.count > args.last:
                self.error_exit('error: --count cannot be larger than --last'
                                ' with --distance=random')
        if args.baseseed == '':
            # Non-reproducibly random
            args.baseseed = None
        random.seed(args.baseseed)

    def main(self, args, inf, ouf):
        """Read `inf`, write to `ouf`, using options `args`."""
        LT = b'<'[0]
        check_posattrs = True
        attrnum = 0
        add_tokennums = self._make_add_tokennums(args)
        next_add_tokennum = next(add_tokennums)
        result = []
        tokencount = 0
        tokennum = 0
        for line in inf:
            if line[0] != LT:
                if tokennum == next_add_tokennum:
                    word = line[:-1].split(b'\t', attrnum + 1)[attrnum]
                    result.append(word)
                    tokencount += 1
                    try:
                        while next_add_tokennum == tokennum:
                            next_add_tokennum = next(add_tokennums)
                    except StopIteration:
                        break
                tokennum += 1
            elif check_posattrs and isbinnames(line):
                attrnum = nameindex(binnamelist(line), b'word')
                check_posattrs = False
        ouf.write(args.separator.encode('utf-8').join(result) + b'\n')

    def _make_add_tokennums(self, args):
        """Return iterator for the numbers of tokens to be output."""

        def make_iter(count, dist, prec=1):
            """Return iterator for `count` int values with approx. `dist` step.

            `dist` may be a float, in which case `prec` is the
            precision with which it is taken ito account.
            """
            return (i // prec for i in range(int(dist * prec - 1),
                                             int(count * dist * prec),
                                             int(dist * prec)))

        def make_random_iter(count, last):
            """Return iterator for `count` random int values in [0, `last`)."""
            # Count cannot be larger than last
            count = min(count, last)
            return iter(sorted(random.sample(range(last), count)))

        if args.distance == DIST_EVEN:
            # Note that "evenly distributed" does not mean "with equal
            # distances", as the distances may differ by one to get an
            # even distribution up to args.last
            return make_iter(args.count, args.last / args.count, 100)
        elif args.distance == DIST_RANDOM:
            return make_random_iter(args.count, args.last)
        else:
            return make_iter(args.count, args.distance)
