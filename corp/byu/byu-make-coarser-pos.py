#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Generate attributes for coarser part-of-speech tags and morphological features
"""


import sys
import argparse
from collections import OrderedDict
from xml.sax.saxutils import escape

from io import open


class CoarserPosGenerator:

    def __init__(self, args):
        self._pos_map = self._read_pos_map_file(args.pos_map_file)
        self._filenames = args.filenames or []
        self._opts = args

    def _read_pos_map_file(self, fname):

        def xml_escape(val):
            return escape(val, {'"': '&quot;', '\'': '&apos;'})

        pos_map = {}
        with open(fname, 'r', encoding='utf8', errors='replace') as f:
            for line in f:
                fields = [field.strip().split('/')[0]
                          for field in line.strip().split('\t')]
                for i in [1, 2]:
                    fields[i] = xml_escape(fields[i])
                pos_map[fields[0]] = (fields[1], fields[2])
                pos_map[xml_escape(fields[0])] = (fields[1], fields[2])
        return pos_map
                
    def process(self):
        if self._filenames:
            for filename in self._filenames:
                with open(filename, 'r', encoding='utf8',
                          errors='replace') as f:
                    self._process_stream(filename, f)
        else:
            self._process_stream('(stdin)', sys.stdin)

    def _process_stream(self, filename, f):
        # sys.stdout.write(repr(self._pos_map))

        def make_featset_value(lst):
            # If all the values of the feature set are the same,
            # output the value only once.
            if len(lst) > 1:
                if all(lst[i] == lst[0] for i in range(1, len(lst))):
                    lst = [lst[0]]
            return '|' + '|'.join(lst) + '|'

        for linenr, line in enumerate(f):
            byu_poses = [field.strip()
                         for field in line.strip().strip('|').split('|')]
            # Python does not have built-in ordered set, so use
            # OrderedDict with dummy values.
            mapped_poses = OrderedDict()
            for byu_pos in byu_poses:
                # sys.stdout.write(byu_pos + '\n')
                # sys.stdout.flush()
                if byu_pos not in self._pos_map:
                    sys.stderr.write(
                        'Warning: Tag {byu_pos} on line {linenr} not found in'
                        ' the mapping; replacing with X\n'
                        .format(byu_pos=byu_pos, linenr=linenr + 1))
                    mapped_poses[('X', '_')] = ''
                else:
                    mapped_poses[self._pos_map[byu_pos]] = ''
            if self._opts.output_stripped_pos:
                sys.stdout.write(make_featset_value(byu_poses) + '\t')
            sys.stdout.write(
                '\t'.join(make_featset_value(
                    [pos_morph[idx] for pos_morph in mapped_poses.keys()])
                          for idx in range(2))
                + '\n')


def getargs():
    argparser = argparse.ArgumentParser(
        description='''Generate attributes for coarser part-of-speech tags and morphological features''')
    argparser.add_argument(
        'pos_map_file',
        help=('File with lines containing the (converted) BYU PoS tag, the'
              ' corresponding coarser PoS tag and morphological features,'
              ' separated tabs'))
    argparser.add_argument(
        'filenames', nargs='*',
        help=('Input files containing the cleaned-up BYU PoS attribute with'
              ' feature set values, typically extracted from the CWB-data with'
              ' cwb-decode'))
    argparser.add_argument(
        '--output-stripped-pos', action='store_true',
        help=('Output the original PoS attribute with trailing spaces removed'
              ' as the first column'))
    return argparser.parse_args()


def main():
    CoarserPosGenerator(getargs()).process()


if __name__ == '__main__':
    main()
