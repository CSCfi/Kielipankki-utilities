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

from collections import defaultdict

import korpimport.util


class GranularityAdjuster(korpimport.util.InputProcessor):

    _month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

    def __init__(self, args=None):
        super(GranularityAdjuster, self).__init__()
        # Adjusting the granularities may collapse several input
        # values into one, so collect the counts first and output them
        # at the end.
        self._counts = defaultdict(int)

    def process_input_stream(self, stream, filename=None):
        self._read_input_stream(stream)
        self._write_output()

    def _read_input_stream(self, stream):
        from_fieldnr = self._opts.from_field
        to_fieldnr = self._opts.to_field
        count_fieldnr = self._opts.count_field
        for line in stream:
            fields = line[:-1].split('\t')
            fields[from_fieldnr] = self._make_from(fields[from_fieldnr])
            fields[to_fieldnr] = self._make_to(fields[to_fieldnr])
            count = fields[count_fieldnr]
            # @COUNT@ will be replaced by the final count when writing
            # output
            fields[count_fieldnr] = u'@COUNT@'
            self._counts['\t'.join(fields)] += int(count)

    def _make_from(self, date):
        datelen = len(date)
        if datelen == 0 or datelen == self._granularity:
            return date
        elif datelen > self._granularity:
            return date[:self._granularity]
        else:
            return date + 'YYYY0101000000'[datelen:self._granularity]

    def _make_to(self, date):
        datelen = len(date)
        if datelen == 0 or datelen == self._granularity:
            return date
        elif datelen > self._granularity:
            return date[:self._granularity]
        elif datelen != 6:
            return date + 'YYYY1231235959'[datelen:self._granularity]
        else:
            return (date + self._get_monthdays(date)
                    + '235959'[:self._granularity - 8])

    def _get_monthdays(self, date):
        mon = int(date[4:6])
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
                 description="""Adjust the granularity of (Korp) timespan
data specified as a starting and
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
        )
        self._granularity = gran_map[self._opts.granularity]
        self._opts.from_field -= 1
        self._opts.to_field -= 1
        self._opts.count_field -= 1


if __name__ == "__main__":
    GranularityAdjuster().run()
