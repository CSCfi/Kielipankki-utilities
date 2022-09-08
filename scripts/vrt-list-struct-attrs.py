#! /usr/bin/env python3
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
        # For each attribute of each structure, a dictionary of two
        # keys: 'basic' for the number of "basic" values and 'featset'
        # for the number of values that can be interpreted as feature
        # set values (beginning and ending with a vertical bar).
        self._struct_attr_value_count = defaultdict(dict)
        self._structname_re = re.compile(r'</?([a-z0-9_-]+)')
        self._attr_re = re.compile(r'''(\S+?)\s*=\s*([\"\'])(.*?)\2''')

    def process_input_stream(self, stream, filename=None):
        for line in stream:
            self._linenr += 1
            mo = self._structname_re.match(line)
            if not mo:
                if line[0] == '<' and line[1] not in '!?':
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
            attrval = mo.group(3)
            attrval_type = ('featset' if (attrval and attrval[0] == '|'
                                          and attrval[-1] == '|')
                            else 'basic')
            if attrname not in self._struct_attrdict[structname]:
                self._struct_attrdict[structname][attrname] = True
                self._struct_attrlist[structname].append(attrname)
                self._struct_attr_value_count[structname][attrname] = {
                    'basic': 0, 'featset': 0 }
            self._struct_attr_value_count[structname][attrname][
                attrval_type] += 1

    def _output_structs(self):
        structspecs = []
        for structname in self._structs:
            structspec = (structname + ':'
                          + str(self._struct_maxdepth[structname] - 1))
            if structname in self._struct_attrlist:
                structspec += (
                    '+' + '+'.join(
                        self._make_attrspec(structname, attrname)
                        for attrname in self._struct_attrlist[structname]))
            structspecs.append(structspec)
        self.output(' '.join(structspecs) + '\n')

    def _make_attrspec(self, structname, attrname):
        attrtype_names = {'featset': 'feature-set',
                          'basic': 'non-feature-set'}
        val_counts = self._struct_attr_value_count[structname][attrname]
        attrtype = ('featset' if val_counts['featset'] > val_counts['basic']
                    else 'basic')
        attrtype_other = 'featset' if attrtype == 'basic' else 'basic'
        if val_counts[attrtype_other] != 0:
            self.warn(
                ('Attribute {attrname} of structure {structname} interpreted'
                 ' as a {attrtype} attribute, even though it has'
                 ' {attrtype_other_count} {attrtype_other} values in addition'
                 ' to {attrtype_count} {attrtype} values.').format(
                     structname=structname, attrname=attrname,
                     attrtype=attrtype_names[attrtype],
                     attrtype_other=attrtype_names[attrtype_other],
                     attrtype_count=val_counts[attrtype],
                     attrtype_other_count=val_counts[attrtype_other]),
                show_fileinfo=False)
        return attrname + ('/' if attrtype == 'featset' else '')

    def getopts(self, args=None):
        self.getopts_basic(
            dict(usage="%prog [input.vrt ...] > output",
                 description=(
"""List the structural attributes (elements and their attributes) in the VRT
input in the format suitable as arguments of the option -S of cwb-encode:
ELEMENT:NESTLEVEL+ATTR1+...+ATTRn. The elements in the input need not be
strictly nested. If most of the values of an attribute begin and end with a
vertical bar ("|...|"), it is interpretede as a feature-set attribute, and
the attribute name is suffixed with a slash in the output.""")
             ),
            args
        )


if __name__ == "__main__":
    StructAttrLister().run()
