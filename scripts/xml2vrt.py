#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

from optparse import OptionParser

from xml2vrt.util import WrappedXMLFileReader
from xml2vrt.converter import Converter, _test_rules
# This is needed only as long as we need to be able to evaluate rules
# read as Python code.
from xml2vrt.rule_ast import *


def getopts():
    optparser = OptionParser()
    optparser.add_option('--rule-file', '--rules', '-r')
    optparser.add_option('--wrapper-elem', '--wrapper-element-name',
                         default=None)
    (opts, args) = optparser.parse_args()
    if opts.wrapper_elem == '':
        opts.wrapper_elem = '__DUMMY__'
    return (opts, args)


def get_rules(opts):
    if opts.rule_file:
        rules = eval(read_file(opts.rule_file))
    else:
        rules = _test_rules
    return rules


def read_file(fname):
    contents = ''
    with codecs.open(fname, 'r', encoding='utf-8') as f:
        for line in f:
            contents += line
    return contents


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    # ElementTree.XMLParser uses the encoding specified in the XML
    # header, so we should not modify it here.
    # sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    # sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    converter = Converter(opts, rules=get_rules(opts))
    converter.process_inputs(args if args else sys.stdin)


if __name__ == "__main__":
    main()
