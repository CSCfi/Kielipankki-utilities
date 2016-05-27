#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
Combine duplicates in the DMA (Digital Morphology Archive) TSV data

For lines having the same parish and text fields, combine the other
fields.

The first line of the input should contain field names and the rest
should be sorted by the parish and text fields.
"""


import sys
import re

import korpimport.util


class DmaDuplicateCombiner(korpimport.util.InputProcessor):

    def __init__(self, args=None):
        super(DmaDuplicateCombiner, self).__init__()
        self._linenr = 0
        self._prev_linenr = 0
        self._dupl_count = {'full': 0, 'subset': 0, 'partial': 0}
        self._combine_fieldnames = [
            ('signum', self._combine_uniq, dict(split=None)),
            ('informant', self._combine_uniq, dict(split='; ')),
            ('comment', self._combine_nonempty, dict()),
            ('location', self._combine_uniq_loc, dict()),
            ('pdf', self._combine_uniq, dict(split=None)),
        ]
        self._duplicate_test_fieldnames = ['parish', 'text']
        self._prev_fields = {}

    def process_input_stream(self, stream, filename=None):
        for linenr, line in enumerate(stream):
            if linenr == 0:
                self._make_fieldname_info(line)
                sys.stdout.write(line)
            else:
                self._linenr = linenr + 1
                processed_line = self._process_line(line)
                if processed_line:
                    sys.stdout.write(processed_line)
        if any(count > 0 for count in self._dupl_count.itervalues()):
            sys.stderr.write(
                u'Removed {0[full]} full and {0[subset]} subset duplicates,'
                u' and combined {0[partial]} partial duplicates\n'
                .format(self._dupl_count))
        sys.stdout.write('\t'.join(self._prev_fields) + '\n')

    def _make_fieldname_info(self, line):
        self._fieldnames = line[:-1].lower().split('\t')
        self._fieldnamenums = dict((val, num)
                                   for num, val in enumerate(self._fieldnames))
        self._duplicate_test_fieldnums = [
            self._fieldnamenums[fieldname]
            for fieldname in self._duplicate_test_fieldnames]
        self._combine_fieldnum_methods = [
            (self._fieldnamenums[fieldname], method, kwargs)
            for fieldname, method, kwargs in self._combine_fieldnames]
        self._combine_fieldnums = [fieldnum for fieldnum, _, _
                                   in self._combine_fieldnum_methods]
        self._fieldnum_comment = self._fieldnamenums['comment']

    def _process_line(self, line):

        def set_prev_info(fields):
            self._prev_fields = fields
            self._prev_linenr = self._linenr
            self._prev_lineinfo = self._lineinfo

        fields = line[:-1].split('\t')
        if fields[self._fieldnum_comment] == '-':
            fields[self._fieldnum_comment] = ''
        self._lineinfo = u'{0} (id {1})'.format(self._linenr, fields[0])
        if not self._prev_fields:
            set_prev_info(fields)
            return None
        if self._is_duplicate(fields):
            self._combine_fields(fields, line)
            return None
        else:
            result = '\t'.join(self._prev_fields) + '\n'
            set_prev_info(fields)
            return result

    def _is_duplicate(self, fields):
        # if len(fields) < 12 or len(self._prev_fields) < 12:
        #     sys.stderr.write('** ' + repr(fields) + repr(self._prev_fields)
        #                      + '\n')
        return (all(fields[fieldnum] == self._prev_fields[fieldnum]
                    for fieldnum in self._duplicate_test_fieldnums)
                and ((fields[self._fieldnum_comment]
                      == self._prev_fields[self._fieldnum_comment])
                     or fields[self._fieldnum_comment] == ''
                     or self._prev_fields[self._fieldnum_comment] == ''))

    def _combine_fields(self, fields, line):
        if all(fields[fieldnum] == self._prev_fields[fieldnum]
               for fieldnum in self._combine_fieldnums):
            sys.stderr.write(
                u'Skipping line {0} as a full duplicate of line {1}:\n{2}'
                .format(self._lineinfo, self._prev_lineinfo, line))
            self._dupl_count['full'] += 1
            return
        sys.stderr.write(u'Combining line {0} to line {1}:\n'
                         .format(self._lineinfo, self._prev_lineinfo))
        comb = False
        for fieldnum, combine_method, kwargs in self._combine_fieldnum_methods:
            prev_val = self._prev_fields[fieldnum]
            if fields[fieldnum] != prev_val:
                self._prev_fields[fieldnum] = combine_method(
                    self._prev_fields[fieldnum], fields[fieldnum], **kwargs)
                if self._prev_fields[fieldnum] != prev_val:
                    sys.stderr.write(
                        u'  Combined {0}: "{1}" + "{2}" => "{3}"\n'
                        .format(self._fieldnames[fieldnum], prev_val,
                                fields[fieldnum], self._prev_fields[fieldnum]))
                    comb = True
        if comb:
            self._dupl_count['partial'] += 1
        else:
            self._dupl_count['subset'] += 1
            sys.stderr.write(u'  Line {0} is a subset of line {1}\n'
                             .format(self._lineinfo, self._prev_lineinfo))

    def _combine_uniq(self, val1, val2, split=None):
        return ' '.join(
            sorted(val for val in set(val1.split(split) + val2.split(split))
                   if val != '-'))

    def _combine_uniq_loc(self, val1, val2):
        if 'SKN ' in val1 or 'SKN ' in val2:
            parts1 = val1.partition('SKN ')
            parts2 = val2.partition('SKN ')
            comb1 = self._combine_uniq(parts1[0], parts2[0])
            return comb1 + 'SKN ' + parts1[2] + '; ' + 'SKN ' + parts2[2]
        else:
            return self._combine_uniq(val1, val2)

    def _combine_nonempty(self, val1, val2):
        return val1 or val2


if __name__ == "__main__":
    DmaDuplicateCombiner().run()
