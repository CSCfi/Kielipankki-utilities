
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
    ]

    def __init__(self):
        super().__init__()

    def main(self, args, inf, ouf):
        """Read `inf`, write to `ouf`, using options `args`."""
        LT = b'<'[0]
        count = args.count
        distance = args.distance
        check_posattrs = True
        attrnum = 0
        splitcount = attrnum + 1
        result = []
        tokencount = 0
        tokennum = 0
        for line in inf:
            if line[0] != LT:
                tokennum += 1
                if tokennum % distance == 0:
                    result.append(line[:-1].split(b'\t', splitcount)[attrnum])
                    tokencount += 1
                    if tokencount == count:
                        break
            elif check_posattrs and isbinnames(line):
                attrnum = nameindex(binnamelist(line), b'word')
                splitcount = attrnum + 1
                check_posattrs = False
        ouf.write(b''.join(result) + b'\n')
