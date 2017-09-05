#! /usr/bin/env python
# -*- coding: utf-8 -*-

#asahala/finclarin
#script for converting OPUS Moses format into VRT

import sys
import vrt_tools

class MOSES_to_VRT_converter:

    def __init__(self):
        self.output = []
        self.data = {}

    def readmoses(self, filename):
        with open(filename, encoding='utf-8') as data:
            self.data = data.readlines()

    def process(self, corpusname, year):
        print('<text title="%s" datefrom="%s0101" dateto="%s1231">' %(corpusname,year,year))
        for line in enumerate(self.data):
            print('<paragraph id="{lineno}">\n{data}\n</paragraph>'\
                  .format(lineno=line[0],
                          data=vrt_tools.tokenize(line[1], 255)))
        print('</text>')

def main(argv):
    if len(sys.argv) < 2:
        print("Usage: mosesvrt.py [inputfile]\n")
        sys.exit(1)
    filename = argv[0]
    year = argv[1]
    j = MOSES_to_VRT_converter()
    j.readmoses(filename)
    j.process(filename, year)

if __name__ == "__main__":
    main(sys.argv[1:])
