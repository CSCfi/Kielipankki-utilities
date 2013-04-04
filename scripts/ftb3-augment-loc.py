#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import re
import codecs
import os.path

from optparse import OptionParser


class OrigFileReader(object):

    _clear_previous_info = False

    def __init__(self, directory=None, encoding='utf-8'):
        self._directory = directory
        self._encoding = encoding
        self._dir_last_part = os.path.split(directory)[1]
        self._fname = None
        self._file = None
        self._linenum = 0
        self._info = {}

    def get_info_for_line(self, fname, linenums):
        self._open_if_new_file(fname)
        if self._clear_previous_info and self._linenum < linenums[-1]:
            self._info = {}
        while self._linenum < linenums[-1]:
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
        (fname_dir, fname) = os.path.split(fname)
        fname_parts = [fname]
        while fname_dir:
            (fname_dir, fname_dir_last_part) = os.path.split(fname_dir)
            if fname_dir_last_part == self._dir_last_part:
                break
            fname_parts[0:0] = [fname_dir_last_part]
        fname_parts[0:0] = [self._directory]
        return os.path.join(*fname_parts)

    def _fill_info_from_line(self, line):
        pass

    def _get_tag_attr(self, line, attrname, default=None):
        mo = re.search(r'<.+\s' + attrname + r'=([^"]+?|".*?")[\s>]', line)
        return mo.group(1).strip('"') if mo else default

    def _get_elem_content(self, line, elemname, default=None):
        mo = re.search(r'<' + elemname + r'(?:\s.*?)?>(.*?)</' + elemname + '>',
                       line)
        return mo.group(1) if mo else default


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
            self._info['type'] = 'speech'
            self._info['speaker_id'] = self._get_tag_attr(line, 'ID')
            self._info['speaker_name'] = self._get_tag_attr(line, 'NAME')
            self._info['language'] = (self._get_tag_attr(line, 'LANGUAGE')
                                      or 'und').lower()
            self._info['p_id'] = str(int(self._info['p_id']) + 1)
        elif line.startswith('<P>'):
            self._info['p_id'] = str(int(self._info['p_id']) + 1)
        elif self._info['type'] == 'chaptertitle':
            self._info['chapter_title'] = line.strip()


class OrigFileReaderJRCAcquis(OrigFileReader):

    _clear_previous_info = True

    def __init__(self, directory=None, encoding='utf-8'):
        OrigFileReader.__init__(self, directory, encoding)

    def _fill_info_from_line(self, line):
        line = line.strip()
        if line.startswith('<teiHeader '):
            self._info = {'type': 'title'}
        elif line.startswith('<title>'):
            title = self._get_elem_content(line, 'title')
            title_key = 'title' if 'codetitle' in self._info else 'codetitle'
            self._info[title_key] = title
        elif line.startswith('<bibl>'):
            url = self._get_elem_content(line, 'xref')
            # The URLs in the files have the older domain europa.eu.int
            url = url.replace('europa.eu.int', 'europa.eu')
            self._info['url'] = url
        elif line.startswith('<p '):
            p_id = self._get_tag_attr(line, 'n')
            if 'type' not in self._info:
                self._info['type'] = 'p'
            if 'p_id' not in self._info:
                self._info['p_id'] = p_id
            else:
                self._info['p_id'] += ',' + p_id


class LocAugmenter(object):

    _origfile_reader_class = {'europarl': OrigFileReaderEuroparl,
                              'jrc': OrigFileReaderJRCAcquis}

    _add_attrs = {'europarl':
                      {'chaptertitle': ['type', 'chapter_id', 'chapter_title',
                                        'p_id'],
                       'speech': ['type', 'speaker_id', 'language',
                                  'speaker_name', 'p_id']},
                  'jrc':
                      {'title': ['title', 'codetitle', 'url', 'p_id'],
                       'p': ['p_id']}
                  }

    def __init__(self, opts):
        self._opts = opts
        self._orig_reader = self._origfile_reader_class[self._opts.source_type](
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
        mo = re.match(r'<s>\s*<loc\s+file="(.+?)"\s+line="(.*?)"\s*/>', line)
        (fname, linenum) = (mo.group(1), mo.group(2))
        info = self._orig_reader.get_info_for_line(fname,
                                                   self._get_linenums(linenum))
        # print fname, linenum, info
        if self._opts.loc_only:
            line = line[3:]
        return self._add_info(line, info)

    def _get_linenums(self, linenum_str):
        return [int(linenum) for linenum in linenum_str.split(',')]

    def _add_info(self, line, info):
        return (line.rstrip(' />\n') + ' '
                + self._make_attributes(
                self._add_attrs[self._opts.source_type][info['type']], info)
                + ' />\n')

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
    optparser.add_option('--source-type', type='choice',
                         choices=['europarl', 'jrc'], default='europarl',
                         help=('Use the source type TYPE: europarl for'
                               ' EuroParl, jrc for JRC Acquis'
                               ' (default: %default)'), metavar='TYPE')
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
