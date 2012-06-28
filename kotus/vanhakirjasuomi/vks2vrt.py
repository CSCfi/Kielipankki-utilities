#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re


from optparse import OptionParser


class OldLiteraryFinnishToVrtConverter(object):

    def __init__(self, opts):
        self._opts = opts
        self._src_code_fields = []
        self._struct_levels = []

    def process_input(self, f):
        prev_fields = dict(zip(self._src_code_fields,
                               [None] * len(self._src_code_fields)))
        sent_nr = 1
        for line in f:
            line = line.strip()
            if line == '':
                continue
            (src_code, line) = line.split(' ', 1)
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
                + '\n'.join([self._make_word_attrs(word)
                             for word in self._split_words(line)]) + '\n'
                + '</sentence>\n')

    def _split_words(self, line):
        return line.split(' ')

    def _make_word_attrs(self, word):
        return word


class BibleToVrtConverter(OldLiteraryFinnishToVrtConverter):

    def __init__(self, opts):
        OldLiteraryFinnishToVrtConverter.__init__(self, opts)
        self._struct_levels = ['work', 'book', 'chapter', 'verse']
        self._src_code_fields = self._struct_levels + ['page']

    def _split_src_code(self, code):
        (work, book, position, page) = code.split('-')
        (chapter, verse) = (position.split(':') if ':' in position
                            else (position, ''))
        return {'work': work,
                'book': book,
                'chapter': chapter,
                'verse': verse,
                'page': page}


class LawsAndSermonsToVrtConverter(OldLiteraryFinnishToVrtConverter):

    def __init__(self, opts, struct_top='source'):
        OldLiteraryFinnishToVrtConverter.__init__(self, opts)
        self._struct_top = struct_top
        self._struct_levels = [struct_top]
        self._src_code_fields = self._struct_levels + ['page']

    def _split_src_code(self, code):
        (law, page) = code.split('-', 1)
        return {self._struct_top: law,
                'page': page}

    def _make_word_attrs(self, word):
        word = word.replace('<', '[').replace('>', ']')
        compl_word = word.replace('~', '')
        orig_word = re.sub(r'.~', '', word)
        return '\t'.join([word, orig_word, compl_word])


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
    elif opts.mode == 'laws':
        converter = LawsAndSermonsToVrtConverter(opts, 'law')
    elif opts.mode == 'sermons':
        converter = LawsAndSermonsToVrtConverter(opts, 'source')
    converter.process_input(sys.stdin)


if __name__ == "__main__":
    main()
