
"""
vrt_scramble.py

The actual implementation of vrt-scramble.

Please run "vrt-scramble -h" for more information.
"""


import sys
import re
import random

from math import floor

from vrtargsoolib import InputProcessor


class VrtScrambler(InputProcessor):

    """Class implementing vrt-scramble functionality."""

    DESCRIPTION = """
    Scramble (randomly shuffle) given structures (elements), such as
    sentences, within larger structures, such as texts, in the VRT
    input and output the scrambled VRT.

    Note that the input may not have intermediate structures between
    the containing structures and the structures to be scrambled; for
    example, if sentences are scrambled within texts, the input may
    not have paragraphs.
    """
    ARGSPECS = [
        ('--scramble-unit|unit = struct "sentence"',
         '''shuffle struct structures (elements)'''),
        ('--scramble-within|within = struct "text"',
         '''shuffle structures within struct structures (elements):
            structures are not moved across struct boundaries'''),
        ('--random-seed|seed = seed "2017"',
         '''set random number generator seed to seed (any string);
            use 0 or "" for a random seed (non-reproducible output)'''),
    ]

    class OPTIONS(InputProcessor.OPTIONS):
        in_as_text = True
        out_as_text = True

    def __init__(self):
        super().__init__()
        self._scramble_units = []

    def check_args(self, args):
        if args.random_seed in ['', '0']:
            args.random_seed = None

    def main(self, args, inf, ouf):
        # version=1 to be compatible with Python 2 random
        random.seed(args.random_seed, version=1)
        within_begin_re = re.compile(
            r'<' + args.scramble_within + '[>\s]')
        scramble_begin_re = re.compile(
            r'<' + args.scramble_unit + '[>\s]')
        scramble_end = '</' + args.scramble_within + '>'
        collecting = False
        units = []
        current_unit = []
        self._linenr = 0
        for line in inf:
            self._linenr += 1
            if collecting:
                if line.startswith(scramble_end):
                    if current_unit:
                        units.append(current_unit)
                    collecting = False
                    for line2 in self._scramble(units):
                        ouf.write(line2)
                    ouf.write(line)
                elif scramble_begin_re.match(line):
                    if current_unit:
                        units.append(current_unit)
                    current_unit = [line]
                elif line.startswith('<') and current_unit == []:
                    mo = re.match(r'<([a-z_0-9]+)', line)
                    struct = ''
                    if mo:
                        struct = mo.group(1)
                    self.error_exit('Structure \'' + struct + '\' between \''
                                    + args.scramble_within + '\' and \''
                                    + args.scramble_unit + '\'')
                else:
                    current_unit.append(line)
            else:
                ouf.write(line)
                if within_begin_re.match(line):
                    units = []
                    current_unit = []
                    collecting = True

    def _scramble(self, units):
        self._random_shuffle(units)
        for unit in units:
            for line in unit:
                yield line

    def _random_shuffle(self, seq):
        """Randomly shuffle seq, same results as Python 2 random.shuffle."""
        # This code was copied from the Python 3.10 library code for
        # random.shuffle. Up to Python 3.10, the same result could be
        # achieved by using random.shuffle(seq, random=random.random),
        # but the parameter random will be removed in Python 3.11
        # (deprecated in 3.9).
        for i in reversed(range(1, len(seq))):
            # pick an element in seq[:i+1] with which to exchange seq[i]
            j = floor(random.random() * (i + 1))
            seq[i], seq[j] = seq[j], seq[i]
