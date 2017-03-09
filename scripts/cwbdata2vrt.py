#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import os.path
import re

from optparse import OptionParser
from subprocess import Popen, PIPE
from xml.sax.saxutils import escape


class CWBDataConverter(object):

    def __init__(self, opts):
        self._opts = opts
        self._cwb_decode = os.path.join(opts.cwbdir, 'cwb-decode')
        if not opts.include_xml_declaration or not opts.include_corpus_element:
            self._ignore_line_re = re.compile(
                '|'.join([(r'<?xml\s'
                           if not opts.include_xml_declaration else ''),
                          (r'<corpus\s|</corpus>'
                           if not opts.include_corpus_element else '')])
                .strip('|'))
        else:
            self._ignore_line_re = None
        self._struct_attr_re = re.compile(
            r'<(?P<elemname>[^_\s]+)'
            r'(?:_(?P<attrname>\S+)\s(?P<attrval>.*))?>\n')
        self._attr_order = self._make_attribute_order()

    def _make_attribute_order(self):
        attr_order = {}
        if self._opts.attribute_order:
            for elemlist in self._opts.attribute_order:
                for elemspec in elemlist.split():
                    elemname, attrstr = re.split(r':(?:\d+\+)?', elemspec)
                    attrs = re.split(r'[+,]', attrstr)
                    attr_order[elemname] = attrs
        return attr_order

    def convert(self, corpora):
        for corpus in corpora:
            self._convert_corpus(corpus)

    def _convert_corpus(self, corpus):

        # Use elem as a namespace so that the inner function
        # write_start_tag can assign to the variables
        class elem:
            name = None
            attrs = []

        def find(seq, item):
            try:
                return seq.index(item)
            except ValueError:
                return -1

        def write_start_tag():
            if elem.name:
                if elem.name in self._attr_order:
                    elem.attrs.sort(
                        key=lambda attr: find(self._attr_order.get(elem.name),
                                              attr[0]))
                sys.stdout.write(
                    '<' + elem.name
                    + ''.join([' ' + name + '="' + escape(val, {'"': '&quot;'})
                               + '"'
                               for name, val in elem.attrs])
                    + '>\n')
            elem.name = None
            elem.attrs = []

        decode = Popen([self._cwb_decode, '-Cx', '-r', self._opts.registry,
                        corpus, '-ALL'], stdout=PIPE)
        for line in iter(decode.stdout.readline, ''):
            if line[0] == '<':
                if self._ignore_line_re and self._ignore_line_re.match(line):
                    continue
                elif line.startswith('</'):
                    # NOTE: This assumes that element names do not
                    # contain underscores
                    if '_' not in line:
                        sys.stdout.write(line)
                else:
                    matchobj = self._struct_attr_re.match(line)
                    if matchobj:
                        groups = matchobj.groupdict()
                        if groups['elemname'] != elem.name:
                            write_start_tag()
                            elem.name = groups['elemname']
                        if groups['attrname']:
                            elem.attrs.append(
                                (groups['attrname'], groups['attrval']))
            else:
                write_start_tag()
                sys.stdout.write(line)


def getopts():
    usage = """%prog [options] corpus ... > corpora.vrt

Convert a corpus or multiple corpora stored in CWB back to the input
VRT format. The output is XML-compatible, except for possible crossing
elements."""
    optparser = OptionParser(usage=usage)
    optparser.add_option(
        '--cwbdir', '-c',
        default=(os.environ.get('CWBDIR') or '/usr/local/cwb/bin'),
        metavar='DIR',
        help='use the cwb-decode binary in DIR (default: %default)')
    optparser.add_option(
        '--registry', '-r',
        default=(os.environ.get('CORPUS_REGISTRY') or '/v/corpora/registry'),
        metavar='DIR',
        help='use DIR as the CWB corpus registry (default: %default)')
    optparser.add_option(
        '--include-xml-declaration', action='store_true',
        help='include XML declaration in the output (omitted by default)')
    optparser.add_option(
        '--include-corpus-element', action='store_true',
        help=('include in the output the top-level "corpus" element added by'
              ' cwb-decode (omitted by default)'))
    optparser.add_option(
        '--attribute-order', action='append', default=[], metavar='ATTRSPEC',
        help=('Order the XML element attributes according to ATTRSPEC.'
              ' The default order is that produced by cwb-decode.'
              ' ATTRSPEC is a space-separated list of S-attribute'
              ' specifications recognized by cwb-encode:'
              ' ELEM:N+ATTR1+ATTR2+..., where ELEM is an element name, N is'
              ' an integer and ATTRn are attribute names.'
              ' Attributes of ELEM are ordered in the order ATTR1, ATTR2, ...'
              ' "N+" is ignored and may be omitted, and ATTRn may be'
              ' separated by a comma instead of a plus.'
              ' This option may be specified multiple times for different'
              ' elements.'))
    opts, args = optparser.parse_args()
    return (opts, args)


def main():
    input_encoding = output_encoding = 'utf-8'
    opts, corpora = getopts()
    converter = CWBDataConverter(opts)
    converter.convert(corpora)


if __name__ == "__main__":
    main()
