#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""Scramble (randomly shuffle) structures in a VRT input."""


# This script has been converted from Python 2 to Python 3.

# TODO:
# - Rewrite the script as a proper VRT tool.


import sys
import re
import random

from math import floor

import korpimport3.util


class VrtScrambler(korpimport3.util.InputProcessor):

    def __init__(self):
        super().__init__()
        self._scramble_units = []
        # version=1 to be compatible with Python 2 random
        random.seed(self._opts.random_seed, version=1)

    def process_input_stream(self, stream, filename=None):
        within_begin_re = re.compile(
            r'<' + self._opts.scramble_within + '[>\s]')
        scramble_begin_re = re.compile(
            r'<' + self._opts.scramble_unit + '[>\s]')
        scramble_end = '</' + self._opts.scramble_within + '>'
        collecting = False
        units = []
        current_unit = []
        for line in stream:
            self._linenr += 1
            if collecting:
                if line.startswith(scramble_end):
                    if current_unit:
                        units.append(current_unit)
                    collecting = False
                    for line2 in self._scramble(units):
                        sys.stdout.write(line2)
                    sys.stdout.write(line)
                elif scramble_begin_re.match(line):
                    if current_unit:
                        units.append(current_unit)
                    current_unit = [line]
                elif line.startswith('<') and current_unit == []:
                    mo = re.match(r'<([a-z_0-9]+)', line)
                    struct = ''
                    if mo:
                        struct = mo.group(1)
                    self.error('Structure \'' + struct + '\' between \''
                               + self._opts.scramble_within + '\' and \''
                               + self._opts.scramble_unit + '\'')
                else:
                    current_unit.append(line)
            else:
                sys.stdout.write(line)
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

    def getopts(self, args=None):
        self.getopts_basic(
            dict(usage="%prog [options] [input] > output",
                 description=(
"""Scramble (randomly shuffle) given structures (elements), such as sentences,
within larger structures, such as texts, in the VRT input and output the
scrambled VRT.

Note that the input may not have intermediate structures between the
containing structures and the structures to be scrambled; for example, if
sentences are scrambled within texts, the input may not have paragraphs.
""")
             ),
            args,
            ['scramble-unit|unit =STRUCT', dict(
                default='sentence',
                help=('shuffle STRUCT structures (elements)'
                      ' (default: %default)'))],
            ['scramble-within|within =STRUCT', dict(
                default='text',
                help=('shuffle structures within STRUCT structures (elements):'
                      ' structures are not moved across STRUCT boundaries'
                      ' (default: %default)'))],
            ['random-seed|seed =SEED', dict(
                default='2017',
                help=('set random number generator seed to SEED (any string);'
                      ' use 0 or "" for a random seed (non-reproducible'
                      ' output) (default: %default)'))],
        )
        if self._opts.random_seed in ['', '0']:
            self._opts.random_seed = None


if __name__ == "__main__":
    VrtScrambler().run()
