#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs


from optparse import OptionParser


class OldLiteraryFinnishToVrtConverter(object):

    _src_code_fields = []
    _struct_levels = []

    def __init__(self, opts):
        self._opts = opts

    def process_input(self, f):
        prev_fields = dict(zip(self._src_code_fields,
                               [None] * len(self._src_code_fields)))
        sent_nr = 1
        for line in f:
            if line == '\n':
                continue
            (src_code, line) = line[:-1].split(' ', 1)
            src_fields = self._split_src_code(src_code)
            sys.stdout.write(self._make_structure(src_fields, prev_fields,
                                                  ('first' if sent_nr == 1
                                                   else 'mid')))
            prev_fields = src_fields
            sys.stdout.write(self._make_sentence(line, sent_nr, src_code,
                                                 src_fields))
            sent_nr += 1
        sys.stdout.write(self._make_structure(src_fields, prev_fields, 'last'))

    def _split_src_code(self, code):
        pass

    def _make_structure(self, src_fields, prev_fields, position='mid'):
        levels = self._struct_levels
        levelcnt = len(levels)
        result = ''
        close_levelnr = levelcnt
        if position == 'last':
            close_levelnr = 0
        else:
            for levelnr in xrange(0, levelcnt):
                level = levels[levelnr]
                if (src_fields[level] != prev_fields[level]
                    and prev_fields[level] is not None):
                    close_levelnr = levelnr
                    break
        # result += 'CLOSE: ' + str(close_levelnr) + '\n'
        for levelnr in xrange(levelcnt - 1, close_levelnr - 1, -1):
            result += '</' + levels[levelnr] + '>\n'
        open_levelnr = 0 if position == 'first' else close_levelnr
        if position != 'last':
            for levelnr in xrange(open_levelnr, levelcnt):
                level = levels[levelnr]
                result += '<' + level + ' code="' + src_fields[level] + '">\n'
        return result

    def _make_sentence(self, line, sent_nr, src_code, src_fields):
        return (u'<sentence id="{0}" code="{1}" page="{2}">\n'
                .format(sent_nr, src_code, src_fields['page'])
                + line.replace(' ', '\n')
                + '</sentence>\n')


class BibleToVrtConverter(OldLiteraryFinnishToVrtConverter):

    _struct_levels = ['work', 'book', 'chapter', 'verse']
    _src_code_fields = ['work', 'book', 'chapter', 'verse', 'page']

    def __init__(self, opts):
        OldLiteraryFinnishToVrtConverter.__init__(self, opts)

    def _split_src_code(self, code):
        (work, book, position, page) = code.split('-')
        (chapter, verse) = (position.split(':') if ':' in position
                            else (position, ''))
        return {'work': work,
                'book': book,
                'chapter': chapter,
                'verse': verse,
                'page': page}


def getopts():
    optparser = OptionParser()
    optparser.add_option('--mode', '-m', type='choice',
                         choices=['biblia', 'laws', 'sermons'],
                         default='biblia')
    (opts, args) = optparser.parse_args()
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    if opts.mode == 'biblia':
        converter = BibleToVrtConverter(opts)
    converter.process_input(sys.stdin)


if __name__ == "__main__":
    main()
