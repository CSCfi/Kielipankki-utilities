#! /usr/bin/env python3


import re

# libpaths adds local library paths to sys.path (korpimport, VRT Tools)
import libpaths

from korpimport import scriptutil
import vrtnamelib


class VRTSplitter(scriptutil.ArgumentRunner):

    DESCRIPTION = """
    Split the texts in the input VRT into yearly files based on the
    date attribute.
    """

    ARGSPECS = [
        ('input_file',
         'input VRT file to be split'),
        ('--output-filename-template|out-template=TEMPL "output-{year}.vrt"'
         ' -> out_templ',
         'output the yearly files with names TEMPL, which should contain'
         ' "{year}" as a placeholder for the year'),
    ]

    def __init__(self):
        super().__init__()

    def main(self):
        out_files = {}
        attr_comment = b''

        def get_year(line):
            return re.search(br'date="([0-9]{4})-', line).group(1)

        def output_text(text, year):
            if year not in out_files:
                out_files[year] = open(
                    self._args.out_templ.format(year=year.decode()), 'wb')
                out_files[year].write(attr_comment)
            for line in text:
                out_files[year].write(line)

        text = []
        year = b''
        with open(self._args.input_file, 'rb') as inf:
            for line in inf:
                if not attr_comment and vrtnamelib.isbinnames(line):
                    attr_comment = line
                else:
                    text.append(line)
                if line.startswith(b'<text '):
                    year = get_year(line)
                if line.startswith(b'</text>'):
                    output_text(text, year)
                    text = []
            for f in out_files.values():
                f.close()


if __name__ == '__main__':
    VRTSplitter().run()
