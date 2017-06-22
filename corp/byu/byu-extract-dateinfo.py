#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Extract date information from URLs.
"""


import sys
import argparse

from io import open

import korpimport.xmlutil as xu
import byu_util


class DateInfoExtractor:

    def __init__(self, args):
        self._filenames = args.filenames or []
        self._opts = args

    def extract(self):
        for filename in self._filenames:
            with open(filename, 'r', encoding='utf8', errors='replace') as f:
                self._extract_dateinfo(filename, f)

    def _extract_dateinfo(self, filename, f):
        for line in f:
            url = line[:-1]
            datefrom = dateto = byu_util.extract_dateinfo_from_url(url)
            year = datefrom[:4]
            sys.stdout.write('\t'.join([datefrom, dateto, year]) + '\n')


def getargs():
    argparser = argparse.ArgumentParser(
        description='''Extract date information from URLs''')
    argparser.add_argument('filenames', nargs='*',
                           help='input files containing one URL per line')
    return argparser.parse_args()


def main():
    args = getargs()
    extractor = DateInfoExtractor(args)
    extractor.extract()


if __name__ == '__main__':
    main()
