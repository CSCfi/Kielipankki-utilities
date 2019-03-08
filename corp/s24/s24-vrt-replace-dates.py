#! /usr/bin/env python3


import os.path
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../../vrt-tools')))
import vrtargsoolib



class DateReplacer(vrtargsoolib.InputProcessor):

    DESCRIPTION = """
    Replace date attributes (date, time, datetime) in text start tags
    with an unspecified date (1970-01-01) in the input VRT file
    corresponding to Suomi24 threads or comments with an approximated
    date in the specified date file. If the date is replaced, add
    attribute datetime_approx="true" else datetime_approx="false".
    """
    ARGSPECS = [
        ('--input-type (threads|comments)',
         'the type of input: threads or comments VRT',
         dict(required=True)),
        ('--date-file=DATE_FILE',
         'A TSV file with thread or comment id and datetime',
         dict(required=True)),
    ]

    def __init__(self):
        super().__init__()
        self._datetimes = {}

    def main(self, args, inf, ouf):

        def append_attr(line, attr):
            # This assumes that the line ends in ">\n", with no trailing
            # whitespace nor \r.
            return line[:-2] + b' ' + attr + line[-2:]

        def search_thread_id(line):
            return re.search(rb'thread="(.*?)"', line)

        def search_comment_id(line):
            return re.search(rb'comment="(.*?)"', line)

        def replace_date(line):
            id_ = search_id(line).group(1)
            date, time = self._datetimes.get(id_)
            line = re.sub(
                rb'date="(.*?)"',
                b'date="' + self._datetimes[id_][0] + b'"', line)
            line = re.sub(
                rb'time="(.*?)"',
                b'time="' + self._datetimes[id_][1] + b'"', line)
            line = re.sub(
                rb'datetime="(.*?)"',
                b'datetime="' + b' '.join(self._datetimes[id_]) + b'"', line)
            return append_attr(line, b'datetime_approx="true"')

        self._read_date_file()
        search_id = (search_thread_id if self._args.input_type == 'threads'
                     else search_comment_id)
        for line in inf:
            if line.rstrip().startswith(b'<text'):
                if b'date="1970' in line:
                    ouf.write(replace_date(line))
                elif b'datetime_approx="' not in line:
                    ouf.write(append_attr(line, b'datetime_approx="false"'))
                else:
                    ouf.write(line)
            else:
                ouf.write(line)

    def _read_date_file(self):
        with open(self._args.date_file, 'rb') as datef:
            for line in datef:
                id_, date, time = line.rstrip().split()
                self._datetimes[id_] = (date, time)


if __name__ == '__main__':
    DateReplacer().run()
