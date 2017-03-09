#! /usr/bin/env python
# -*- coding: utf-8 -*-


# This script implements similar functionality to "xmlstats.py
# --cwb-struct-attrs" but the input need not be valid XML: for
# example, the elements need not be strictly nested.


import sys
import re

from collections import defaultdict

import korpimport.util


class StructAttrLister(korpimport.util.InputProcessor):

    def __init__(self, args=None):
        super(StructAttrLister, self).__init__()
        self._structs = []
        self._struct_depth = defaultdict(int)
        self._struct_maxdepth = defaultdict(int)
        # We could use collections.OrderedDict but that requires
        # Python 2.7. Would it be faster than using a separate list
        # for order?
        self._struct_attrdict = defaultdict(dict)
        self._struct_attrlist = defaultdict(list)
        self._structname_re = re.compile(r'</?([a-z0-9_-]+)')
        self._attr_re = re.compile(r'''(\S+?)\s*=\s*([\"\']).*?\2''')

    def process_input_stream(self, stream, filename=None):
        for line in stream:
            self._linenr += 1
            mo = self._structname_re.match(line)
            if not mo:
                if line[0] == '<':
                    self.warn('Literal "<" at the beginning of a non-tag line: '
                              + line.rstrip('\n'))
                continue
            structname = mo.group(1)
            if structname not in self._struct_depth:
                self._structs.append(structname)
            if line[1] == '/':
                self._struct_depth[structname] -= 1
            else:
                self._struct_depth[structname] += 1
                self._struct_maxdepth[structname] = max(
                    self._struct_maxdepth[structname],
                    self._struct_depth[structname])
                self._extract_attrs(structname, line)
        self._output_structs()

    def _extract_attrs(self, structname, line):
        attriter = self._attr_re.finditer(line)
        for mo in attriter:
            attrname = mo.group(1)
            if attrname not in self._struct_attrdict[structname]:
                self._struct_attrdict[structname][attrname] = True
                self._struct_attrlist[structname].append(attrname)

    def _output_structs(self):
        structspecs = []
        for structname in self._structs:
            structspec = (structname + ':'
                          + str(self._struct_maxdepth[structname] - 1))
            if structname in self._struct_attrlist:
                structspec += '+' + '+'.join(self._struct_attrlist[structname])
            structspecs.append(structspec)
        self.output(' '.join(structspecs) + '\n')

    def getopts(self, args=None):
        self.getopts_basic(
            dict(usage="%progname [input.vrt ...] > output",
                 description=(
"""List the structural attributes (elements and their attributes) in the VRT
input in the format suitable as arguments of the option -S of cwb-encode:
ELEMENT:NESTLEVEL+ATTR1+...+ATTRn. The elements in the input need not be
strictly nested.""")
             ),
            args
        )


if __name__ == "__main__":
    StructAttrLister().run()
