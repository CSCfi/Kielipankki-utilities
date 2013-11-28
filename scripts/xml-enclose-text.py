#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

import os.path

from optparse import OptionParser


class LineMarker(object):

    def __init__(self, opts, input_encoding):
        self._opts = opts
        self._input_encoding = input_encoding
        self._elem_id = 1

    def process_files(self, fnames):
        for fname in fnames or ['-']:
            self._process_file(fname)

    def _process_file(self, fname):
        if fname != '-':
            with codecs.open(fname, 'r', encoding=self._input_encoding) as f:
                self._mark_lines(f)
        else:
            self._mark_lines(sys.stdin)

    def _mark_lines(self, file_):
        for line in file_:
            if line[0] in '<\n':
                sys.stdout.write(line)
            else:
                sys.stdout.write(self._add_line_tags(line))

    def _add_line_tags(self, line):
        result = (u'<{elemname} id="{id}">\n{line}</{elemname}>\n'
                  .format(elemname=self._opts.element, line=line,
                          id=self._elem_id))
        self._elem_id += 1
        return result


def getopts():
    optparser = OptionParser()
    optparser.add_option('--element')
    (opts, args) = optparser.parse_args()
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    line_marker = LineMarker(opts, input_encoding)
    line_marker.process_files(args)


if __name__ == "__main__":
    main()
