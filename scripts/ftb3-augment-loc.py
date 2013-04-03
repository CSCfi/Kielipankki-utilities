#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import re
import codecs

from optparse import OptionParser


class OrigFileReader(object):

    def __init__(self, directory=None, encoding='utf-8'):
        self._directory = directory
        self._encoding = encoding
        self._fname = None
        self._file = None
        self._linenum = 0
        self._info = {}

    def get_info_for_line(self, fname, linenum):
        self._open_if_new_file(fname)
        while self._linenum < linenum:
            line = self._file.readline()
            self._linenum += 1
            self._fill_info_from_line(line)
        return self._info

    def _open_if_new_file(self, fname):
        if fname != self._fname:
            if self._file:
                self._file.close()
            self._file = codecs.open(self._make_filename(fname),
                                     encoding=self._encoding)
            self._fname = fname
            self._linenum = 0

    def _make_filename(self, fname):
        return (self._directory + '/' if self._directory else '') + fname

    def _fill_info_from_line(self, line):
        pass

    def _get_tag_attr(self, line, attrname, default=None):
        mo = re.match(r'<.+\s' + attrname + r'=([^"]+?|".*?")[\s>]', line)
        return mo.group(1).strip('"') if mo else default


class OrigFileReaderEuroparl(OrigFileReader):

    def __init__(self, directory=None, encoding='utf-8'):
        OrigFileReader.__init__(self, directory, encoding)

    def _fill_info_from_line(self, line):
        if line.startswith('<CHAPTER'):
            self._info = {}
            self._info['type'] = 'chaptertitle'
            self._info['chapter_id'] = self._get_tag_attr(line, 'ID')
            self._info['p_id'] = '1'
        elif line.startswith('<SPEAKER'):
            self._info['type'] = 'speaker'
            self._info['speaker_id'] = self._get_tag_attr(line, 'ID')
            self._info['speaker_name'] = self._get_tag_attr(line, 'NAME')
            self._info['language'] = (self._get_tag_attr(line, 'LANGUAGE')
                                      or 'und').lower()
        elif line.startswith('<P>'):
            self._info['p_id'] = str(int(self._info['p_id']) + 1)


class LocAugmenter(object):

    def __init__(self, opts):
        self._opts = opts
        self._orig_reader = OrigFileReaderEuroparl(
            directory=self._opts.original_file_directory)

    def print_augmented(self, files):
        for line in self.get_augmented(files):
            sys.stdout.write(line)

    def get_augmented(self, files):
        for file_ in files:
            named_file = isinstance(file_, basestring)
            if named_file:
                file_ = codecs.open(file_, encoding='utf-8')
            try:
                while True:
                    try:
                        yield next(self._read_and_augment(file_))
                    except StopIteration:
                        break
            finally:
                if named_file:
                    file_.close()

    def _read_and_augment(self, file_):
        orig_fname = ''
        orig_linenum = 0
        for line in file_:
            if line.startswith('<s><loc '):
                yield self._make_info_line(line)
            elif not self._opts.loc_only:
                yield line

    def _make_info_line(self, line):
        mo = re.match(r'<s><loc file=".+/([^/]+)" line="(.*?)"/>', line)
        (fname, linenum) = (mo.group(1), mo.group(2))
        info = self._orig_reader.get_info_for_line(fname, int(linenum))
        # print fname, linenum, info
        if self._opts.loc_only:
            line = line[3:]
        return self._add_info(line, info)

    def _add_info(self, line, info):
        add_attrs = {'chaptertitle': ['type', 'chapter_id'],
                     'speaker': ['type', 'speaker_id', 'language',
                                 'speaker_name', 'p_id']}
        return (line.rstrip('/>\n') + ' '
                + self._make_attributes(add_attrs[info['type']], info)
                + '/>\n')

    def _make_attributes(self, names, valuedict):
        return ' '.join([u'{name}="{val}"'.format(name=name,
                                                  val=valuedict.get(name, ''))
                         for name in names])


def getopts():
    usage = """%prog [options] [FTB3_file ...]
Augment loc elements in FinnTreeBank 3 with extra attributes containing
information available in the original files."""
    optparser = OptionParser(usage=usage)
    optparser.add_option('--original-file-directory',
                         help='Original aligned files are in DIR',
                         metavar='DIR')
    optparser.add_option('--loc-only', action='store_true',
                         help=('Output only the augmented loc elements, '
                               'not all the input'))
    (opts, args) = optparser.parse_args()
    return (opts, args)


def main():
    sys.stdin = codecs.getreader('utf-8')(sys.stdin)
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)
    (opts, args) = getopts()
    augmenter = LocAugmenter(opts)
    augmenter.print_augmented(args or [sys.stdin])


if __name__ == '__main__':
    main()
