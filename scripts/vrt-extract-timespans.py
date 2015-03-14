#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

from optparse import OptionParser
# collections.OrderedDict requires Python 2.7
from collections import defaultdict, OrderedDict
from datetime import date
from subprocess import Popen, PIPE


def get_current_year():
    return date.today().year


def get_current_year2():
    return get_current_year() % 100


def get_current_century():
    return get_current_year() / 100


class TimespanExtractor(object):

    DEFAULT_PATTERN_PARTS = {
        'Y': ur'(?P<Y>(?:1[0-9]|20)[0-9][0-9])',
        'Y2': ur'(?P<Y>(?:1[0-9]|20)?[0-9][0-9])',
        'M': ur'(?P<M>0?[1-9]|1[0-2])',
        'D': ur'(?P<D>0?[1-9]|[12][0-9]|3[01])'
        }
    PART_SEP_PATTERN = ur'[-./]'
    RANGE_SEP_PATTERN = ur'\s*[-/–]\s*'
    DATE_GRAN_RANGES = [(1000, get_current_year()), (1, 12), (1, 31),
                        (0, 24), (0, 59), (0, 59)]
    MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    class PattDict(dict):

        # A separate class to make it easier to use with defaultdict

        def __init__(self):
            dict.__init__(self)
            self['base'] = []
            self['end'] = []

    def __init__(self, opts):
        self._opts = opts
        if self._opts.fixed:
            self._opts.fixed = re.split(r'[-/–\s]+', self._opts.fixed, 1)
            if len(self._opts.fixed) == 1:
                self._opts.fixed.append('')
            self._opts.fixed = tuple(self._opts.fixed)
        elif not self._opts.unknown:
            self._extract_patterns = defaultdict(self.PattDict)
            self._make_extract_patterns(self._opts.extract_pattern,
                                        pattern_type='base')
            self._make_extract_patterns(self._opts.end_extract_pattern,
                                        pattern_type='end')
            # print self._extract_patterns
            self._make_excludes()
        self._time_tokencnt = defaultdict(int)
        self._curr_century = str(get_current_century())
        self._prev_century = str(get_current_century() - 1)

    def _make_extract_patterns(self, patterns, pattern_type='base'):

        def add_regex_group(regex):
            # Enclose regex in parentheses if it does not contain
            # (capturing) groups
            if ('(?P<' not in regex
                and re.match(r'^(?:[^(\\]|\\.|\(\?)+$', regex)):
                return '(' + regex + ')'
            else:
                return regex

        is_base_pattern = (pattern_type == 'base')
        default_pattern = self._make_default_pattern(
            allow_range=is_base_pattern)
        if is_base_pattern and patterns == []:
            patterns.append('* * ' + default_pattern)
        for source in patterns:
            parts = source.split(None, 2)
            elemnames = parts[0].split('|')
            attrnames = parts[1].split('|') if len(parts) > 1 else ['*']
            pattern = (add_regex_group(parts[2]) if len(parts) > 2
                       else default_pattern)
            for elemname in elemnames:
                for attrname in attrnames:
                    self._extract_patterns[elemname][pattern_type].append(
                        (attrname, pattern))

    def _make_default_pattern(self, allow_range=True):
        # FIXME: Make patterns work with ranges with partial dates,
        # such as 2014-09-10/15, 2014-09-10/10-12, 10.-15.9.2014,
        # 10.9.-12.10.2014
        if self._opts.two_digit_years:
            self.DEFAULT_PATTERN_PARTS['Y'] = self.DEFAULT_PATTERN_PARTS['Y2']
        if self._opts.full_dates:
            if self._opts.full_date_order == 'ymd':
                # YMD pattern has optional component separators but
                # obligatory leading zeros in month and day.
                patt = (self.DEFAULT_PATTERN_PARTS['Y']
                        + '(?:(?:' + self.PART_SEP_PATTERN + ')?'
                        + self.DEFAULT_PATTERN_PARTS['M'].replace('0?', '0')
                        + '(?:(?:' + self.PART_SEP_PATTERN + ')?'
                        + self.DEFAULT_PATTERN_PARTS['D'].replace('0?', '0')
                        + ')?)?')
            else:
                patt = self.PART_SEP_PATTERN.join(
                    self.DEFAULT_PATTERN_PARTS[datechar]
                    for datechar in self._opts.full_date_order.upper())
        else:
            patt = self.DEFAULT_PATTERN_PARTS['Y']
        patt = '(' + patt + ')'
        if allow_range and self._opts.ranges:
            patts = {'1': '', '2': ''}
            for pattnr in ['1', '2']:
                patts[pattnr] = re.sub(r'<([YMDhms])>',
                                       r'<\g<1>' + pattnr + '>', patt)
            patt = (patts['1'] + '(?:' + self.RANGE_SEP_PATTERN
                    + patts['2'] + ')?')
        return patt

    def _make_excludes(self):
        self._excludes = defaultdict(list)
        for exclude in self._opts.exclude:
            parts = exclude.split(None, 2)
            elemnames = parts[0].split('|')
            attrnames = parts[1].split('|') if len(parts) > 1 else ['*']
            for elemname in elemnames:
                self._excludes[elemname].extend(attrnames)

    def process_files(self, files):
        if isinstance(files, list):
            for file_ in files:
                self._process_file(file_)
        else:
            self._process_file(files)
        if 'extract' in self._opts.mode:
            self.output_timespans(
                self._opts.timespans_output_file or sys.stdout)

    def _process_file(self, fname):
        if isinstance(fname, basestring):
            with codecs.open(fname, 'r', encoding='utf-8') as f:
                self._extract_timespans(f)
        else:
            self._extract_timespans(fname)

    def _extract_timespans(self, f):
        # NOTE: This does not allow an end time in a different
        # structure than the start time. Would it be needed?
        time = ('', '')
        # The name of the structure containing time information
        timestruct = None
        # Allow for nested time structures
        timestruct_depth = 0
        for line in f:
            if self._opts.unknown or self._opts.fixed:
                if not line.startswith('<'):
                    self._time_tokencnt[time] += 1
            elif timestruct and line.startswith('</' + timestruct + '>'):
                timestruct_depth -= 1
                if timestruct_depth == 0:
                    time = ('', '')
                    timestruct = None
            elif line.startswith('<'):
                if not timestruct:
                    time = self._opts.fixed or self._extract_time(line)
                    if time[1] < time[0]:
                        time = (time[0], time[0])
                    if time[0]:
                        timestruct = re.match(r'<(\S+)', line).group(1)
                        timestruct_depth += 1
                        if 'add' in self._opts.mode:
                            datefrom, dateto = self._make_output_dates(time,
                                                                       'add')
                            line = (line[:-2] + (' datefrom="{0}" dateto="{1}"'
                                                 .format(datefrom, dateto))
                                    + line[-2:])
                elif line.startswith('<' + timestruct + ' '):
                    timestruct_depth += 1
            else:
                self._time_tokencnt[time] += 1
            if 'add' in self._opts.mode:
                sys.stdout.write(line)

    def _extract_time(self, line):
        if '*' in self._excludes.get('*', []):
            return ('', '')
        mo = re.match(r'<(.*?)( .*)?>', line)
        if not mo or not mo.group(2):
            return ('', '')
        elemname = mo.group(1)
        if '*' in self._excludes.get(elemname, []):
            return ('', '')
        attrlist = mo.group(2)
        attrs = OrderedDict(re.findall(r' (.*?)="(.*?)"', attrlist))
        real_elemname = elemname
        if not elemname in self._extract_patterns:
            elemname = '*'
        start_time, end_time = self._extract_time_patt(
            real_elemname, attrs, self._extract_patterns[elemname]['base'])
        if not end_time:
            end_time1, end_time2 = self._extract_time_patt(
                real_elemname, attrs, self._extract_patterns[elemname]['end'])
            # Prefer matching P<Y2> over P<Y>
            end_time = end_time2 or end_time1
        return (start_time, end_time)

    def _extract_time_patt(self, real_elemname, attrs, extract_patterns):
        for (patt_attr, pattern) in extract_patterns:
            if patt_attr in attrs:
                check_attrs = [patt_attr]
            elif patt_attr == '*':
                check_attrs = attrs.iterkeys()
            else:
                continue
            for attrname in check_attrs:
                if (attrname in self._excludes.get(real_elemname, [])
                    or attrname in self._excludes.get('*', [])):
                    continue
                date = self._extract_time_regex(pattern, attrs[attrname])
                if date[0] or date[1]:
                    return date
        return ('', '')

    def _extract_time_regex(self, regex, value):
        # print regex, value
        mo = re.search(regex, value)
        if mo:
            named_groups = mo.groupdict()
            # print named_groups
            if named_groups:
                start_date_parts = [(named_groups.get(part, '')
                                     or named_groups.get(part + '1', ''))
                                    for part in 'YMD']
                end_date_parts = [named_groups.get(part + '2', '') or ''
                                  for part in 'YMD']
                # Handle ellipsed year and/or month. This does not
                # currently work with the default patterns.
                if any(end_date_parts):
                    end_date_parts = [
                        end_date_parts[partnr] or start_date_parts[partnr]
                        for partnr in xrange(3)]
                start_date = '-'.join(start_date_parts).rstrip('-')
                end_date = '-'.join(end_date_parts).rstrip('-')
            else:
                start_date = mo.group(1)
                if self._opts.ranges and len(mo.groups()) > 1:
                    end_date = mo.group(2)
                else:
                    end_date = ''
            if start_date:
                start_date = self._fix_date(start_date, 
                                            keep_order=bool(named_groups))
            if end_date:
                end_date = self._fix_date(end_date,
                                          keep_order=bool(named_groups))
            return (start_date, end_date)
        return ('', '')

    def _fix_date(self, datestr, keep_order=True):
        datestr = datestr.strip()
        if self._opts.full_dates:
            date_parts = [part for part in re.split(r'[ -./T]+', datestr)
                          if part != '']
            if not keep_order and self._opts.full_date_order != 'ymd':
                date_parts_ordered = [
                    date_parts[self._opts.full_date_order.index(part)]
                    for part in 'ymd']
                date_parts = date_parts_ordered
            if self._opts.two_digit_years:
                date_parts[0] = self._fix_year(date_parts[0])
            for (partnr, part) in enumerate(date_parts):
                gran_range = self.DATE_GRAN_RANGES[partnr]
                if not gran_range[0] <= int(part) <= gran_range[1]:
                    return ''
                if len(part) == 1:
                    date_parts[partnr] = '0' + part
            return ''.join(date_parts)
        elif self._opts.two_digit_years:
            return self._fix_year(datestr)
        else:
            return datestr

    def _fix_year(self, year):
        if self._opts.two_digit_years and len(year) == 2:
            return (self._prev_century if int(year) > self._opts.century_pivot
                    else self._curr_century) + year
        else:
            return year

    def output_timespans(self, outfname):
        if not isinstance(outfname, basestring):
            self._write_timespans(outfname)
        else:
            compress_prog = {'bz2': 'bzip2', 'gz': 'gzip'}.get(
                outfname.rpartition('.')[-1], None)
            with open(outfname, 'wb') as real_outfile:
                if compress_prog:
                    pipe = Popen(compress_prog, stdin=PIPE, stdout=real_outfile,
                                 close_fds=True)
                    outfile = pipe.stdin
                else:
                    outfile = real_outfile
                self._write_timespans(outfile)

    def _write_timespans(self, outfile):
        prefix = ([self._opts.timespans_prefix] if self._opts.timespans_prefix
                  else [])
        for (time, tokencnt) in sorted(self._time_tokencnt.iteritems()):
            outfile.write(
                '\t'.join(prefix
                          + list(self._make_output_dates(time, 'extract'))
                          + [str(tokencnt)])
                + '\n')

    def _make_output_dates(self, date, mode):
        start_date, end_date = date
        end_date = end_date or start_date
        if mode in self._opts.output_full_dates:
            if len(start_date) == 4:
                start_date += '0101'
            elif len(start_date) == 6:
                start_date += '01'
            if len(end_date) == 4:
                end_date += '1231'
            elif len(end_date) == 6:
                end_date += self._get_month_days(end_date)
        return (start_date, end_date)

    def _get_month_days(self, year_month_str):
        month = int(year_month_str[4:])
        month_days = self.MONTH_DAYS[month - 1]
        if self.MONTH_DAYS == 28:
            year = int(year_month_str[:4])
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                month_days = 29
        return str(month_days)


def getopts():
    optparser = OptionParser()
    optparser.add_option('--unknown', action='store_true', default=False)
    optparser.add_option('--fixed', default=None)
    optparser.add_option('--extract-pattern', '--pattern',
                         '--begin-extract-pattern', '--begin-pattern',
                         action='append', default=[])
    optparser.add_option('--end-extract-pattern', '--end-pattern',
                         action='append', default=[])
    optparser.add_option('--two-digit-years', action='store_true',
                         default=False)
    optparser.add_option('--exclude', action='append', default=[])
    optparser.add_option('--century-pivot', type='int',
                         default=get_current_year2())
    optparser.add_option('--full-dates', action='store_true', default=False)
    optparser.add_option('--full-date-order', type='choice',
                         choices=['ymd', 'dmy', 'mdy'], default='ymd')
    optparser.add_option('--ranges', action='store_true')
    optparser.add_option('--mode', type='choice',
                         choices=['extract', 'add', 'add+extract'],
                         default='extract')
    optparser.add_option('--timespans-output-file')
    optparser.add_option('--timespans-prefix')
    optparser.add_option('--output-full-dates', type='choice',
                         choices=['extract', 'add', 'add+extract', 'always'])
    (opts, args) = optparser.parse_args()
    if not opts.output_full_dates:
        opts.output_full_dates = ''
    elif opts.output_full_dates == 'always':
        opts.output_full_dates = 'add+extract'
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    extractor = TimespanExtractor(opts)
    extractor.process_files(args if args else sys.stdin)


if __name__ == "__main__":
    main()
