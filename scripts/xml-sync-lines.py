#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

import os.path

from optparse import OptionParser


class TextSynchronizer(object):

    def __init__(self, opts, input_encoding):
        self._opts = opts
        self._input_encoding = input_encoding
        self._sync_elems = set(self._opts.sync_elements.split())
        self._add_elems = set(self._opts.add_elements.split())
        self._ref_file = None
        self._addelem_linebuffer = []
        self._elemstack = []
        
    def sync_lines(self, fnames):
        if len(fnames) < 2:
            fnames.append('-')
        with codecs.open(fnames[0],
                         encoding=self._input_encoding) as self._ref_file:
            for fname in fnames[1:]:
                self._sync_lines(fname)

    def _sync_lines(self, fname):
        if fname == '-':
            self._sync_lines_input(sys.stdin)
        else:
            with codecs.open(fname, encoding=self._input_encoding) as f:
                self._sync_lines_input(f)

    def _sync_lines_input(self, file_):
        for line in file_:
            if line.strip().startswith('<'):
                self._sync_struct_line(line)
            else:
                self._sync_text_line(line)

    def _sync_struct_line(self, line):
        elemname, tagtype = self._extract_elemname(line)
        if elemname in self._sync_elems:
            self._read_ref_file_until(line)
        else:
            elemname, tagtype = self._extract_elemname(line)
            if tagtype == 'start':
                self._elem_start(elemname)
                sys.stdout.write(line)
            else:
                self._elem_end(elemname, True)

    def _sync_text_line(self, line):
        self._read_ref_file_until(line)

    def _read_ref_file_until(self, line):
        # print "RR", line
        ref_line = None
        while ref_line != '' and ref_line != line:
            ref_line = self._ref_file.readline()
            elemname, tagtype = self._extract_elemname(ref_line)
            # print "Ref", elemname, tagtype, ref_line
            if elemname in self._add_elems:
                self._process_addelem_line(elemname, tagtype, ref_line)
            elif ref_line == line:
                self._flush_addelem_buffer()
                sys.stdout.write(ref_line)
            
    def _process_addelem_line(self, elemname, tagtype, line):
        # print "PAEL", elemname, tagtype, line
        if tagtype == 'start':
            self._addelem_linebuffer.append((elemname, line))
        elif tagtype == 'end':
            if (self._addelem_linebuffer
                and self._addelem_linebuffer[-1][0] == elemname):
                self._addelem_linebuffer.pop()
            else:
                self._elem_end(elemname, True)

    def _flush_addelem_buffer(self):
        # print "FL", self._addelem_linebuffer
        for elemname, line in self._addelem_linebuffer:
            self._elem_start(elemname)
            sys.stdout.write(line)

    def _elem_start(self, elemname):
        # print "S", elemname, self._elemstack
        self._elem_end(elemname, True)
        self._elemstack.append(elemname)

    def _elem_end(self, elemname=None, output=False):
        # print "E", elemname, output, self._elemstack
        if elemname and elemname not in self._elemstack:
            return
        while self._elemstack:
            stack_elemname = self._elemstack.pop()
            if output:
                sys.stdout.write('</' + stack_elemname + '>\n')
            if elemname is None or elemname == stack_elemname:
                break

    def _extract_elemname(self, line):
        mo = re.match('\s*<(/?)([-\w:]+)', line)
        if mo:
            return (mo.group(2), 'end' if mo.group(1) == '/' else 'start')
        else:
            return (None, None)


def getopts():
    optparser = OptionParser()
    optparser.add_option('--sync-elements')
    optparser.add_option('--add-elements')
    optparser.add_option('--skip-empty-add-elements')
    (opts, args) = optparser.parse_args()
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    syncer = TextSynchronizer(opts, input_encoding)
    syncer.sync_lines(args)


if __name__ == "__main__":
    main()
