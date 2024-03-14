
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
        ('--unit = struct "sentence"',
         '''shuffle struct structures (elements)'''),
        ('--within = struct "text"',
         '''shuffle structures within struct structures (elements):
            structures are not moved across struct boundaries'''),
        ('--seed = seed',
         '''set random number generator seed to seed (any string)
            (default: "" = non-reproducible output)''',
         dict(default='')),
        ('--legacy',
         '''produce the same result as the old vrt-scramble.py for any
            non-empty seed'''),
    ]

    def __init__(self):
        super().__init__()

    def check_args(self, args):
        if args.seed == '':
            args.seed = None

    def main(self, args, inf, ouf):
        if args.legacy:
            seed_ver = 1
            self._random_shuffle = self._random_shuffle_legacy
        else:
            seed_ver = 2
            self._random_shuffle = random.shuffle
        random.seed(args.seed, version=seed_ver)
        within_begin_re = re.compile(
            (r'<' + args.within + '[>\s]').encode('UTF-8'))
        scramble_begin_re = re.compile(
            (r'<' + args.unit + '[>\s]').encode('UTF-8'))
        scramble_end = ('</' + args.within + '>').encode('UTF-8')
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
                elif line.startswith(b'<') and current_unit == []:
                    mo = re.match(br'<([a-z_0-9]+)', line)
                    struct = ''
                    if mo:
                        struct = mo.group(1)
                    self.error_exit('Structure \'' + struct.decode('UTF-8')
                                    + '\' between \''
                                    + args.within + '\' and \''
                                    + args.unit + '\'')
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

    def _random_shuffle_legacy(self, seq):
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
