#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys

from optparse import OptionParser


def add_sentence_tags(file_, opts):
    para_start = '<' + opts.paragraph_element_name + '>\n'
    para_end = '</' + para_start[1:]
    sent_start = '<' + opts.sentence_element_name + '>\n'
    sent_end = '</' + sent_start[1:]
    para_marker_line_start = '1\t' + opts.paragraph_marker + '\t'
    in_para = False
    in_sent = False
    sys.stdout.write('<' + opts.top_element_name + '>\n')
    for line in file_:
        if line.strip() == '':
            if in_sent:
                sys.stdout.write(sent_end)
                in_sent = False
        elif line.startswith(para_marker_line_start):
            if in_para:
                sys.stdout.write(para_end)
            sys.stdout.write(para_start)
            in_para = True
        else:
            if not in_sent:
                sys.stdout.write(sent_start)
                in_sent = True
            sys.stdout.write(line)
    if in_sent:
        sys.stdout.write(sent_end)
    if in_para:
        sys.stdout.write(para_end)
    sys.stdout.write('</' + opts.top_element_name + '>\n')


def getopts():
    optparser = OptionParser()
    optparser.add_option('--sentence-element-name', '--sent-elem-name',
                         default='sentence')
    optparser.add_option('--paragraph-element-name', '--para-elem-name',
                         default='paragraph')
    optparser.add_option('--top-element-name', '--top-elem-name',
                         default='text')
    optparser.add_option('--paragraph-marker', '--para-marker',
                         default='<p>')
    opts, args = optparser.parse_args()
    return opts, args


def main():
    opts, args = getopts()
    if args:
        for fname in args:
            with open(fname) as f:
                add_sentence_tags(f, opts)
    else:
        add_sentence_tags(sys.stdin, opts)


if __name__ == '__main__':
    main()
