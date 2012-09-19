#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

from optparse import OptionParser


def getopts():
    optparser = OptionParser()
    optparser.add_option('--tokenize', default=False)
    optparser.add_option('--add-links', '--add-link-elements', default=False)
    (opts, args) = optparser.parse_args()
    return (opts, args)


def process_input(args, opts, input_encoding):
    if len(args) > 0:
        for fname in args:
            with codecs.open(fname, 'r', encoding=input_encoding) as f:
                process_file(f, opts)
    else:
        process_file(sys.stdin, opts)


def process_file(f, opts):
    sentnr = 1
    for line in f:
        sys.stdout.write('<sentence id="' + str(sentnr) + '">\n')
        if opts.add_links:
            sys.stdout.write('<link id="' + str(sentnr) + '">\n')
        sys.stdout.write(tokenize(line[:-1], opts))
        if opts.add_links:
            sys.stdout.write('</link>\n')
        sys.stdout.write('</sentence>\n')
        sentnr += 1


def tokenize(text, opts):
    text = text or ''
    if opts.tokenize:
        text = re.sub(r'([.?!,:])(")', r'\1 \2', text)
        text = re.sub(r'(\.\.\.)([,:;?!")])', r' \1 \2', text)
        text = re.sub(r'([.,:;?!")]|\.\.\.)([ \n]|\Z)', r' \1\2', text)
        text = re.sub(r'([ \n]|\A)(["(])', r'\1\2 ', text)
    return '\n'.join(text.split()) + '\n'


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    process_input(args, opts, input_encoding)


if __name__ == "__main__":
    main()
