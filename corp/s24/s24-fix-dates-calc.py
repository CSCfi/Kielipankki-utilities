#! /usr/bin/env python3


# FIXME: The script has very little error checking


import os.path
import sys

from collections import defaultdict
from datetime import datetime as dt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../../scripts/korpimport')))
import scriptutil


class DateApproximator(scriptutil.ArgumentRunner):

    DESCRIPTION = """
    Calculate approximate dates for Suomi24 messages dated 1970-01-01, based on
    the preceding and following message. The messages in the input files must
    be sorted numerically by thread id.
    """
    ARGSPECS = [
        ('threads_file',
         'a TSV file with thread id and datetime'),
        ('comments_file',
         'a TSV file with comment id, datetime, parent comment id, thread id'),
        ('--output-prefix=PREFIX "./fixed-dates-"',
         'prefix output files with PREFIX'),
    ]
    _datatypes = ['threads', 'comments']
    _datetime_format = '%Y-%m-%d %H:%M:%S'

    class _Data:

        def __init__(self, fname,
                     add_extra_info_fn=None,
                     test_add_extra_data_fn=None,
                     add_extra_data_fn=None,
                     get_alt_preceding_date_fn=None,
                     get_alt_following_date_fn=None):
            self.fname = fname
            self.undated = set()
            self.undated_neighbours = defaultdict(list)
            self.data = {}
            self.add_extra_info_fn = add_extra_info_fn
            self.test_add_extra_data_fn = test_add_extra_data_fn
            self.add_extra_data_fn = add_extra_data_fn
            self.get_alt_preceding_date_fn = get_alt_preceding_date_fn
            self.get_alt_following_date_fn = get_alt_following_date_fn
            self.approx_dates = {}

    def __init__(self):
        super().__init__()
        self._data = {
            'threads': self._Data(
                self._args.threads_file,
                test_add_extra_data_fn=(
                    lambda fields: fields[0] in self._undated_comment_threads),
                get_alt_following_date_fn=self._get_thread_alt_following_date),
            'comments': self._Data(
                self._args.comments_file,
                add_extra_info_fn=self._add_comment_extra_info,
                test_add_extra_data_fn=lambda fields: (
                    fields[0] in self._undated_comment_parents
                    or (fields[3] in self._data['threads'].undated
                        and fields[2] == b'0'
                        and fields[3] not in
                        self._undated_thread_first_comments)),
                add_extra_data_fn=self._add_thread_first_comment,
                get_alt_preceding_date_fn=self._get_comment_alt_preceding_date,
                ),
            }
        self._undated_comment_threads = set()
        self._undated_comment_parents = set()
        self._undated_thread_first_comments = {}

    def _get_thread_alt_following_date(self, thread_id):
        return (
            self._data['comments']
            .data.get(self._undated_thread_first_comments.get(thread_id, b'0'),
                      [b'9999'])[0])

    def _get_comment_alt_preceding_date(self, comment_id):
        comment_data = self._data['comments'].data[comment_id]
        return max(
            self._data['threads'].data[comment_data[2]][0],
            self._data['comments'].data.get(comment_data[1], [b''])[0])

    def main(self):
        for datatype in self._datatypes:
            undated = self._read_undated_ids(
                self._data[datatype].fname,
                self._data[datatype].add_extra_info_fn
                )
            self._data[datatype].undated = undated
            # print(undated)
            if not undated:
                self.warn('No undated {datatype} in {fname}'.format(
                    datatype=datatype, fname=self._data[datatype].fname))
        # print(self._undated_comment_threads, self._undated_comment_parents,
        #       self._undated_thread_first_comments)
        if any(self._data[datatype].undated for datatype in self._datatypes):
            for datatype in self._datatypes:
                self._read_data(self._data[datatype])
                # print(datatype, self._data[datatype].data)
            # print(self._undated_thread_first_comments)
            # A separate for loop is needed, as the data for both threads and
            # comments needs to be read for approximating the dates.
            for datatype in self._datatypes:
                self._make_approximate_dates(self._data[datatype])
                self._write_file(datatype, self._data[datatype])

    def _read_undated_ids(self, fname, handle_rest_fn=None):
        result = set()
        with open(fname, 'rb') as inf:
            for line in inf:
                fields = line.rstrip().split(b'\t')
                if fields[1].startswith(b'1970-01-01'):
                    result.add(fields[0])
                    if handle_rest_fn is not None:
                        handle_rest_fn(fields)
        return result

    def _add_comment_extra_info(self, fields):
        if fields[2] != b'0':
            self._undated_comment_parents.add(fields[2])
        self._undated_comment_threads.add(fields[3])

    def _read_data(self, data):
        extra_test_fn = data.test_add_extra_data_fn
        extra_add_fn = data.add_extra_data_fn
        with open(data.fname, 'rb') as inf:
            fields_prev = None
            add_next = False
            # Note that this only works if the 1970-01-01 dates are not
            # consecutive in the file and neither the first nor the last one.
            for line in inf:
                fields = line.rstrip().split(b'\t')
                # print(fields, extra_test_fn(fields))
                if fields[0] in data.undated:
                    data.data[fields_prev[0]] = fields_prev[1:]
                    data.data[fields[0]] = fields[1:]
                    data.undated_neighbours[fields[0]].append(fields_prev[1])
                    add_next = True
                elif add_next:
                    data.data[fields[0]] = fields[1:]
                    data.undated_neighbours[fields_prev[0]].append(fields[1])
                    add_next = False
                elif (extra_test_fn is not None and extra_test_fn(fields)):
                    # if len(fields) > 2:
                    #     print(fields[3] in self._data['threads'].undated,
                    #           fields[2] == b'0',
                    #           fields[3] not in self._undated_thread_first_comments)
                    data.data[fields[0]] = fields[1:]
                    if extra_add_fn is not None:
                        extra_add_fn(fields)
                fields_prev = fields

    def _add_thread_first_comment(self, fields):
        if fields[3] in self._data['threads'].undated and fields[2] == b'0':
            self._undated_thread_first_comments.setdefault(
                fields[3], fields[0])
            # print(self._undated_thread_first_comments)

    def _make_approximate_dates(self, data):
        datetime_format = self._datetime_format

        def make_timestamp(date_bytes):
            return (
                dt.strptime(date_bytes.decode(), datetime_format).timestamp())

        def calc_mean_datetime(date1, date2):
            return (dt.fromtimestamp(round((make_timestamp(date1)
                                            + make_timestamp(date2)) / 2))
                    .strftime(datetime_format)
                    .encode())

        get_alt_preceding_date_fn = (
            data.get_alt_preceding_date_fn or (lambda x: b''))
        get_alt_following_date_fn = (
            data.get_alt_following_date_fn or (lambda x: b'9999'))
        for id_ in sorted(data.undated, key=lambda x: int(x)):
            preceding = max(data.undated_neighbours[id_][0],
                            get_alt_preceding_date_fn(id_))
            following = min(data.undated_neighbours[id_][1],
                            get_alt_following_date_fn(id_))
            data.approx_dates[id_] = calc_mean_datetime(preceding, following)
            # print(id_, data.undated_neighbours[id_],
            #       get_alt_preceding_date_fn(id_),
            #       get_alt_following_date_fn(id_), preceding, following,
            #       data.approx_dates[id_])

    def _write_file(self, datatype, data):
        with open(self._args.output_prefix + datatype + '.tsv', 'wb') as outf:
            for id_, date in sorted(data.approx_dates.items(),
                                    key=lambda x: int(x[0])):
                outf.write(id_ + b'\t' + date + b'\n')


if __name__ == '__main__':
    DateApproximator().run()
