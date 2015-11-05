#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Scramble the sentences in a VRT input."""


# TODO: Add options: scramble unit, within, random seed


import sys
import re
import random

import korpimport.util


class VrtScrambler(korpimport.util.InputProcessor):

    def __init__(self):
        super(VrtScrambler, self).__init__()
        self._scramble_unit = 'sentence'
        self._scramble_within = 'text'
        self._scramble_units = []
        self._rnd = random.Random(2015)

    def process_input_stream(self, stream, filename=None):
        within_begin_re = re.compile(ur'<' + self._scramble_within + '[>\s]')
        scramble_begin_re = re.compile(ur'<' + self._scramble_unit + '[>\s]')
        scramble_end = '</' + self._scramble_within + '>'
        collecting = False
        units = []
        current_unit = []
        for line in stream:
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
                else:
                    current_unit.append(line)
            else:
                sys.stdout.write(line)
                if within_begin_re.match(line):
                    units = []
                    current_unit = []
                    collecting = True

    def _scramble(self, units):
        self._rnd.shuffle(units)
        for unit in units:
            for line in unit:
                yield line


if __name__ == "__main__":
    VrtScrambler().run()
