#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

import os.path

from optparse import OptionParser


class EuroparlXMLifier(object):

    def __init__(self, opts, input_encoding):
        self._opts = opts
        self._input_encoding = input_encoding
        self._outfile = sys.stdout
        self._elem_stack = []
        self._sent_id = 1

    def process_files(self, fnames):
        for fname in fnames or ['-']:
            self._process_file(fname)

    def _process_file(self, fname):
        if self._opts.text_element:
            self._elem_start(self._opts.text_element,
                             [('filename', os.path.basename(fname))])
        if fname != '-':
            with codecs.open(fname, 'r', encoding=self._input_encoding) as f:
                self._process_input(f)
        else:
            self._process_input(sys.stdin)
        if self._opts.text_element:
            self._elem_end(self._opts.text_element)
        elif self._elem_stack:
            self._elem_end(self._elem_stack[0])

    def _process_input(self, file_):
        for line in file_:
            if line[0] == '<':
                if line[1] == '/':
                    self._elem_end(line.strip('</ \t\n'))
                else:
                    self._process_struct_line(line)
            elif line != '\n' or not self._opts.remove_empty_lines:
                self._process_text_line(line)

    def _process_struct_line(self, line):
        elemname = re.match(r'<(\w+)', line).group(1).lower()
        attrs = re.findall(r'(\w+)=(\w+|"[^"]*")', line)
        attrs = [(name.lower(), val[1:-1] if val[0] == '"' else val)
                 for name, val in attrs]
        self._elem_end('p')
        # Do not add p tags to avoid empty paragraphs (<P> sometimes
        # occurs immediately before another tag)
        if elemname != 'p':
            self._elem_start(elemname, attrs)

    def _process_text_line(self, line):
        if self._elem_stack[-1] != 'p':
            self._elem_start('p')
        if self._opts.sentence_element:
            line = self._add_sentence_tags(line)
        self._outfile.write(line)

    def _add_sentence_tags(self, text):
        sents = text.rstrip('\n').split('\n')
        return ''.join(self._add_sentence_tags_single(sent) for sent in sents)

    def _add_sentence_tags_single(self, sent):
        result = (self._make_start_tag(self._opts.sentence_element,
                                       [('id', self._sent_id)])
                  + '\n' + sent + '\n'
                  + self._make_end_tag(self._opts.sentence_element)
                  + '\n')
        self._sent_id += 1
        return result

    def _elem_start(self, elemname, attrs=None):
        attrs = attrs or []
        self._elem_end(elemname)
        self._outfile.write(self._make_start_tag(elemname, attrs) + '\n')
        self._elem_stack.append(elemname)

    def _elem_end(self, elemname=None):
        if elemname and elemname not in self._elem_stack:
            return
        while self._elem_stack:
            stack_elemname = self._elem_stack.pop()
            self._outfile.write(self._make_end_tag(stack_elemname) + '\n')
            if elemname is None or elemname == stack_elemname:
                break

    def _make_start_tag(self, elemname, attrs):
        return ('<' + ' '.join([elemname]
                               + [u'{name}="{val}"'.format(name=name, val=val)
                                  for (name, val) in attrs])
                + '>')

    def _make_end_tag(self, elemname):
        return '</' + elemname + '>'


def getopts():
    optparser = OptionParser()
    optparser.add_option('--remove-empty-lines', action='store_true')
    optparser.add_option('--text-element')
    optparser.add_option('--sentence-element')
    (opts, args) = optparser.parse_args()
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    xmlifier = EuroparlXMLifier(opts, input_encoding)
    xmlifier.process_files(args)


if __name__ == "__main__":
    main()
