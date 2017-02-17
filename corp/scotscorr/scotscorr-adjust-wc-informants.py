#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Adjust word counts in a ScotsCorr informant information file."""


import re

import korpimport.util as korputil


class WordCountAdjuster(korputil.InputProcessor):

    def __init__(self):
        super(WordCountAdjuster, self).__init__()
        self._letter_info = {}
        self._read_wordcount_file()
        
    def _read_wordcount_file(self):
        for line in korputil.tsv_dictreader(self._opts.word_count_file):
            self._letter_info[line['fn']] = line

    def process_input_stream(self, stream, filename=None):

        def get_value(line):
            mo = re.match(r'%\S+?:\s*(.+?)\s*$', line)
            return mo.group(1) if mo else ""

        for line in stream:
            self._linenr += 1
            if line.startswith('%FN:'):
                fname = get_value(line[:-1])
            elif line.startswith('%WC:'):
                if fname in self._letter_info:
                    line = '%WC: ' + self._letter_info[fname]['wc_new'] + '\n'
                else:
                    self.warn('Cannot find information for letter ' + fname)
            self.output(line)

    def getopts(self, args=None):
        self.getopts_basic(
            dict(usage="%prog [options] [input] > output",
                 description=(
"""Adjust the word count parameters (%WC) in the input containing
ScotsCorr informant information in plain text format, based on a
letter information file.
""")
             ),
            args,
            ['word-count-file =FILE', dict(
                help=('read letter word count information from the FILE'
                      ' (tab-separated values with a heading row)'))],
        )
        if self._opts.word_count_file is None:
            self.error('Please specify the word count file with'
                       ' --word-count-file', show_fileinfo=False)


if __name__ == "__main__":
    WordCountAdjuster().run()
