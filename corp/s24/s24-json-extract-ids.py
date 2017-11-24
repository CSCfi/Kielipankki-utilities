#! /usr/bin/env python

# Extract thread and comment ids along with date and time from Suomi24
# JSON data.
#
# Usage: s24-json-extract-ids.py s24_data.json ... > s24_ids.tsv
#
# The input are Suomi24 JSON files and the output a TSV file with four
# fields: thread id, comment id ("_" if the start of a thread), date
# (yyyymmdd) and time (hhmmss).
#
# Jyrki Niemi, FIN-CLARIN, 2017-11-24


import sys
import json
import time


def main(fnames):
    for fname in fnames:
        with open(fname) as f:
            data = json.load(f)
            extract_ids(data)


def extract_ids(data):

    def make_time(created_at):
        if created_at is None:
            return '\t'
        else:
            return time.strftime('%Y%m%d\t%H%M%S',
                                 time.localtime(created_at / 1000))

    for item in data:
        sys.stdout.write(
            '\t'.join([
                str(item.get('thread_id', '_')),
                str(item.get('comment_id', '_')),
                make_time(item.get('created_at'))])
            + '\n')
        if 'comments' in item:
            extract_ids(item['comments'])


if __name__ == '__main__':
    main(sys.argv[1:])
