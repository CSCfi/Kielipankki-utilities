#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
Adjust the granularity of (Korp) timespan data

The timespans are specified as a starting and ending value in the
format YYYYMMDDhhmmss or a prefix of that. A count field is associated
with each timespan and it is adjusted accordingly, if the granularity
adjustments collapse multiple timespan values to the same. Possible
other fields are passed through intact. The fields are separated by
tabs.
"""


import sys
import re

from collections import defaultdict

import korpimport.util


class GranularityAdjuster(korpimport.util.InputProcessor):

    _month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

    def __init__(self, args=None):
        super(GranularityAdjuster, self).__init__()
        # Adjusting the granularities may collapse several input
        # values into one, so collect the counts first and output them
        # at the end (unless --no-counts).
        self._counts = defaultdict(int)

    def process_input_stream(self, stream, filename=None):
        self._read_input_stream(stream)
        if not self._opts.no_counts:
            self._write_output()

    def _read_input_stream(self, stream):
        from_fieldnr = self._opts.from_field
        to_fieldnr = self._opts.to_field
        count_fieldnr = self._opts.count_field
        counts = not self._opts.no_counts
        for line in stream:
            fields = line[:-1].split('\t')
            new_from = self._make_date(fields[from_fieldnr], 'from')
            new_to = self._make_date(fields[to_fieldnr], 'to')
            if new_from == '' or new_to == '':
                new_from = new_to = ''
            fields[from_fieldnr] = new_from
            fields[to_fieldnr] = new_to
            if counts:
                count = fields[count_fieldnr]
                # @COUNT@ will be replaced by the final count when writing
                # output
                fields[count_fieldnr] = u'@COUNT@'
                self._counts['\t'.join(fields)] += int(count)
            else:
                sys.stdout.write('\t'.join(fields) + '\n')

    def _make_date(self, date, type_):
        date = date.strip()
        if not date:
            return date
        datelen = len(date)
        # TODO: Check the validity of the date more precisely
        if date and not re.match(r'^([0-9][0-9]){2,7}$', date):
            # Return empty for invalid values
            sys.stderr.write('Invalid date' + type_ + ': ' + date + '\n')
            return ''
        elif datelen == 0 or datelen == self._granularity:
            return date
        elif datelen > self._granularity:
            return date[:self._granularity]
        elif type_ == 'from':
            return date + 'YYYY0101000000'[datelen:self._granularity]
        elif datelen != 6:
            return date + 'YYYY1231235959'[datelen:self._granularity]
        else:
            return (date + self._get_monthdays(date)
                    + '235959'[:self._granularity - 8])

    def _get_monthdays(self, date):
        mon = int(date[4:6])
        if mon < 1 or mon > 12:
            sys.stderr.write('Invalid month in date: ' + date + '\n')
            return '00'
        mdays = self._month_days[mon - 1]
        if mdays == 28:
            year = int(date[:4])
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                mdays += 1
        return str(mdays)

    def _write_output(self):
        for key in self._counts.iterkeys():
            sys.stdout.write(
                key.replace(u'@COUNT@', unicode(self._counts[key])) + '\n')

    def getopts(self, args=None):
        gran_map = {
            'year': 4,
            'y': 4,
            'month': 6,
            'mon': 6,
            'm': 6,
            'day': 8,
            'd': 8,
            'hour': 10,
            'h': 10,
            'minute': 12,
            'min': 12,
            'n': 12,
            'second': 14,
            'sec': 14,
            's': 14
        }
        self.getopts_basic(
            dict(usage="%progname [options] [input] > output",
                 description="""Adjust the granularity of (Korp) timespan data specified as a starting and
ending value in the format YYYYMMDDhhmmss or a prefix of that. A count
field is associated with each timespan and adjusted accordingly, if
the granularity adjustments collapse multiple timespan values into the
same. Possible other fields are passed through intact. The fields are
separated by tabs."""
             ),
            args,
            ['--granularity', dict(
                type='choice',
                choices=['year', 'y',
                         'month', 'mon', 'm',
                         'day', 'd',
                         'hour', 'h',
                         'minute', 'min', 'n',
                         'second', 'sec', 's'],
                default='day',
                metavar='GRAN',
                help=('output time data at granularity GRAN: year (y),'
                      ' month (mon, m), day (d), hour (h), minute (min, n)'
                      ' or second (sec, s) (default: %default)'))],
            ['--from-field', dict(
                type='int', default=2, metavar='N',
                help=('field N contains the timespan starting value'
                      ' (default: %default)'))],
            ['--to-field', dict(
                type='int', default=3, metavar='N',
                help=('field N contains the timespan ending value'
                      ' (default: %default)'))],
            ['--count-field', dict(
                type='int', default=4, metavar='N',
                help=('field N contains the timespan count'
                      ' (default: %default)'))],
            ['--no-counts', dict(
                action='store_true',
                help='the input does not contain a count field')],
        )
        self._granularity = gran_map[self._opts.granularity]
        self._opts.from_field -= 1
        self._opts.to_field -= 1
        self._opts.count_field -= 1


if __name__ == "__main__":
    GranularityAdjuster().run()
