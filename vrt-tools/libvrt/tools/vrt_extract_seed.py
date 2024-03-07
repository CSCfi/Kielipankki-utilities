
"""
vrt_extract_seed.py

The actual implementation of vrt-extract-seed.

Please run "vrt-extract-seed -h" for more information.
"""


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
         '''the distance between the words to extract''',
         dict(type=posint, default=100)),
        ('--separator = sep',
         '''separate words in output with sep''',
         dict(default='')),
    ]

    def __init__(self):
        super().__init__()

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
                    result.append(line[:-1].split(b'\t', attrnum + 1)[attrnum])
                    tokencount += 1
                    try:
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
        return iter(
            range(args.distance - 1, args.count * args.distance, args.distance))
