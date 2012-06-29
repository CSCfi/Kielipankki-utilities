#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

import xml.etree.ElementTree as et

from optparse import OptionParser


class Converter(object):

    def __init__(self, opts):
        self._opts = opts

    def process_input(self, f):
        self._src_etr = et.parse(f)
        result_etr = self._convert()
        result_etr.write(sys.stdout, encoding='utf-8')

    def _convert(self):
        text_e = et.Element("text")
        self._add_text_info(text_e)
        self._add_body(text_e)
        self._add_content_newlines(text_e)
        return et.ElementTree(text_e)

    def _add_text_info(self, text_e):
        text_e.set("title", self._get_title())
        text_e.set("distributor", self._get_distributor())
        text_e.set("source", self._get_source())

    def _get_title(self):
        return self._src_etr.find("teiHeader//title").text.strip()

    def _get_distributor(self):
        return ' / '.join([distr.text.strip() for distr in
                           self._src_etr.findall("teiHeader//distributor")])

    def _get_source(self):
        return self._src_etr.find("teiHeader//sourceDesc/p").text.strip()

    def _add_body(self, text_e):
        body_roots = self._src_etr.findall(".//text/body")
        text_e.extend([subresult
                       for elem in body_roots
                       for subresult in self._process_body_elem(elem)])

    def _process_body_elem(self, body_e):
        result = None
        id_attr = body_e.get('id', '')
        # print '<' + body_e.tag + " id=" + id_attr
        if body_e.tag in ['p', 'head', 'opener']:
            result = et.Element('sentence')
            self._process_mixed_content(body_e, result)
            result.set('type', body_e.tag)
        elif body_e.tag == 'div':
            type_ = body_e.get('type', '')
            subresults = [subresult
                          for subelem in body_e
                          for subresult in self._process_body_elem(subelem)]
            if not type_:
                return subresults
            else:
                tag = {'artikla': 'article', u'pykälä': 'paragraph'}[type_]
                result = et.Element(tag)
                # result.set('type', type_)
                result.extend(subresults)
                # print len(result)
        elif body_e.tag == 'body':
            return self._process_body_elem(body_e[0])
        result.set('id', id_attr)
        self._add_content_newlines(result)
        # print "<<" + result.text + ">>"
        # print '>' + body_e.tag + " id=" + id_attr + " " + result.get('id')
        return [result]

    def _process_text(self, elem, result):
        result.text = self._tokenize(self._get_all_text(elem))

    def _process_mixed_content(self, elem, result):
        result.text = self._tokenize(elem.text)
        result.tail = self._tokenize(elem.tail)
        result.attrib = elem.attrib
        self._add_content_newlines(result)
        for subelem in elem:
            subresult = et.Element(subelem.tag)
            self._process_mixed_content(subelem, subresult)
            result.append(subresult)

    def _get_all_text(self, elem):
        return elem.text + ''.join([self._get_all_text(subelem) + subelem.tail
                                    for subelem in elem])

    def _tokenize(self, text):
        text = re.sub(r'([.,:;])[ \n]', r' \1 ', text)
        return '\n'.join(text.split()) + '\n'

    def _add_content_newlines(self, elem):
        elem.text = elem.text or ''
        if not elem.text.startswith('\n'):
            elem.text = '\n' + elem.text
        elem.tail = elem.tail or ''
        if not elem.tail.endswith('\n'):
            elem.tail += '\n'


def getopts():
    optparser = OptionParser()
    optparser.add_option('--mode', '-m', type='choice',
                         choices=['statute'],
                         default='statute')
    (opts, args) = optparser.parse_args()
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    # ElementTree.XMLParser uses the encoding specified in the XML
    # header, so we should not modify it here.
    # sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    # sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    converter = Converter(opts)
    converter.process_input(args[0] if args else sys.stdin)


if __name__ == "__main__":
    main()
