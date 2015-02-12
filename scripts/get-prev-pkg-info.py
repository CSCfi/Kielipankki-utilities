#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

from optparse import OptionParser
from datetime import datetime


def read_info_file(fname, opts):
    # Info file fields, tab separated: epoch, ISO date, Hg revision
    with open(fname, 'r') as f:
        info = ('0', '', '0')
        prev_info = info
        for line in f:
            prev_info = info
            info = tuple(line[:-1].split('\t'))
    overwrite = check_overwrite(opts, int(info[0]))
    return (overwrite, (prev_info if overwrite else info))


def check_overwrite(opts, timestamp):
    if opts.overwrite == 'days':
        now = datetime.today()
        prev = datetime.fromtimestamp(timestamp)
        timedelta = now - prev
        return (timedelta.total_seconds() <= opts.overwrite_days * 24 * 60 * 60)
    else:
        return (opts.overwrite == 'yes')
    

def getopts():
    optparser = OptionParser()
    optparser.add_option('--overwrite', type='choice',
                         choices=['yes', 'no', 'days'], default='days')
    optparser.add_option('--overwrite-days', type='int', default=7)
    (opts, args) = optparser.parse_args()
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    (overwrite, info) = read_info_file(args[0], opts)
    sys.stdout.write('\t'.join(['yes' if overwrite else 'no']
                               + list(info)) + '\n')


if __name__ == "__main__":
    main()
