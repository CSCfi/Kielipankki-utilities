#! /usr/bin/env python

# Convert Suomi24 JSON data to TSV.
#
# Usage: s24-json-extract-ids.py [--output-fields fieldlist]
#                                s24_data.json ... > s24_ids.tsv
#
# The input are Suomi24 JSON files and the output a TSV file with the
# fields listed below in _all_fields (or as specified with
# --output-fields). The fields "date" and "time" are derived from
# "created_at".
#
# Jyrki Niemi, FIN-CLARIN, 2017-11-27


import sys
import json
import time
import re

import korpimport.util as korputil


class Suomi24JsonToTsvConverter(korputil.InputProcessor):

    # TODO: Add some fields only present in newer JSON data
    _all_fields = [
        'thread_id',
        'comment_id',
        'created_at',
        'date',
        'time',
        # topiclist contains the topics separated by vertical bars
        'topiclist',
        'title',
        'anonnick',
        'user_id',
        'username',
        'deleted',
        'closed',
        'closed_reason',
        'modified',
        'modifier_role',
        'parent_comment_id',
        'quote_id',
        'views',
        'body',
    ]
    # Fields inherited from the top of the thread
    _inherited_fields = [
        'title',
        'topiclist',
        'closed',
        'closed_reason',
        'views',
    ]

    def __init__(self):
        super(Suomi24JsonToTsvConverter, self).__init__()
        self._top = True

    def process_input_stream(self, stream, filename=None):
        if self._top:
            sys.stdout.write(u'\t'.join(self._output_fields) + '\n')
            self._top = False
        data = json.load(stream)
        self._convert(data)

    def _convert(self, data, inherited=None):

        def add_time(item):
            created_at = item.get('created_at')
            if not created_at:
                item['date'] = item['time'] = ''
            else:
                timestamp = time.localtime(created_at / 1000)
                item['date'] = time.strftime('%Y%m%d', timestamp)
                item['time'] = time.strftime('%H%M%S', timestamp)

        def convert_spaces(item, key):
            item[key] = (item.get(key, '').replace('\n', '&#x0A;')
                         .replace('\r', '&#x0D;').replace('\t', '&#x09;'))

        for item in data:
            if inherited:
                for inherited_field in self._inherited_fields:
                    item.setdefault(inherited_field,
                                    inherited.get(inherited_field, ''))
            add_time(item)
            if 'user_info' in item:
                item.update(item['user_info'])
            if 'topics' in item:
                item['topiclist'] = u'|'.join(topic['title'].strip()
                                              for topic in item['topics'])
            if 'comment_id' not in item:
                item['comment_id'] = '_'
            for key in ['body', 'title', 'anonnick']:
                convert_spaces(item, key)
            sys.stdout.write(u'\t'.join(unicode(item.get(key, ''))
                                        for key in self._output_fields)
                             + '\n')
            if 'comments' in item:
                self._convert(item['comments'], item)

    def getopts(self, args=None):
        self.getopts_basic(
            dict(usage='%prog [input.json ...] > output.tsv',
                 description='Extract Suomi24 JSON data to TSV.'),
            args,
            ['output-fields =FIELDLIST', dict(
                help=('Output the fields listed in FIELDLIST, fieldnames'
                      ' separated by whitepace or commas'))]
        )
        if not self._opts.output_fields:
            self._output_fields = self._all_fields
        else:
            self._output_fields = re.split(r'[\s,]+', self._opts.output_fields)


if __name__ == '__main__':
    Suomi24JsonToTsvConverter().run()
