#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import re

import korpimport.util


class PlaceNameAdder(korpimport.util.InputProcessor):

    def __init__(self, args=None):
        super(PlaceNameAdder, self).__init__()

    def process_input_stream(self, stream, filename=None):
        src_struct_starttag = '<' + self._src_struct + ' '
        src_struct_endtag = '</' + self._src_struct + '>'
        placename = ''
        sent_first_token = False
        extract_attr_re = re.compile(
            r'\s' + self._src_attr + r'=(["\'])(.*?)\1')
        for line in stream:
            if line.startswith(src_struct_starttag):
                mo = extract_attr_re.search(line)
                if mo:
                    placename = mo.group(2)
            elif line.startswith(src_struct_endtag):
                placename = ''
            elif line.startswith('<sentence'):
                sent_first_token = True
            elif not line.startswith('<'):
                if sent_first_token and placename:
                    line = '\t'.join([line[:-1], placename, self._opts.pos_tag,
                                      '']) + '\n'
                    sent_first_token = False
                else:
                    line = '\t'.join([line[:-1], self._opts.dummy_value,
                                      self._opts.dummy_value, '']) + '\n'
            sys.stdout.write(line)
                
    def getopts(self, args=None):
        self.getopts_basic(
            dict(usage="%prog [options] [input] > output",
                 description=(
"""Add place names in the structural attributes to positional attributes in
the form recognized by Korp's map feature: the first token of each sentece
has a place name lemma extracted from the structural attributes and a part of
speech recognized by Korp's map. All other tokens of sentences get dummy
values. An empty msd attribute is also added.
This only works for data that has no lemma and POS information.
""")
             ),
            args,
            ['--source-attribute', dict(
                metavar='ATTRSPEC',
                help=('get the place name from the structural attribute'
                      ' specified by ATTRSPEC, which is of the form STRUCT_ATTR'
                      ' where STRUCT is a structure (element) and ATTR its'
                      ' attribute'))],
            ['--pos-tag', dict(
                default='PM', metavar='TAG',
                help='mark the place name with POS tag TAG')],
            ['--dummy-value', dict(
                default='_', metavar='DUMMY',
                help='use DUMMY as the dummy lemma and POS tag')]
        )
        if not self._opts.source_attribute:
            sys.stderr.write('Please specify --source-attribute\n')
            exit(1)
        self._src_struct, self._src_attr = re.split(
            r'[_.:]', self._opts.source_attribute, 1)


if __name__ == "__main__":
    PlaceNameAdder().run()
