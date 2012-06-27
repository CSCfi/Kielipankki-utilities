#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs


from optparse import OptionParser


def process_input(f):
    prev_fields = {'work': None, 'book': None, 'chapter': None, 'verse': None,
                   'page': None}
    sent_nr = 1
    for line in f:
        (src_code, line) = line[:-1].split(' ', 1)
        src_fields = split_src_code(src_code)
        sys.stdout.write(make_structure(src_fields, prev_fields,
                                        ('first' if sent_nr == 1 else 'mid')))
        prev_fields = src_fields
        sys.stdout.write(make_sentence(line, sent_nr, src_code, src_fields))
        sent_nr += 1
    sys.stdout.write(make_structure(src_fields, prev_fields, 'last'))



def split_src_code(code):
    (work, book, position, page) = code.split('-')
    (chapter, verse) = (position.split(':') if ':' in position
                        else (position, ''))
    return {'work': work,
            'book': book,
            'chapter': chapter,
            'verse': verse,
            'page': page}


def make_structure(src_fields, prev_fields, position='mid'):
    levels = ['work', 'book', 'chapter', 'verse']
    result = ''
    close_levelnr = len(levels)
    if position == 'last':
        close_levelnr = 0
    else:
        for levelnr in xrange(0, len(levels)):
            level = levels[levelnr]
            if (src_fields[level] != prev_fields[level]
                and prev_fields[level] is not None):
                close_levelnr = levelnr
                break
    # result += 'CLOSE: ' + str(close_levelnr) + '\n'
    for levelnr in xrange(len(levels) - 1, close_levelnr - 1, -1):
        result += '</' + levels[levelnr] + '>\n'
    open_levelnr = 0 if position == 'first' else close_levelnr
    if position != 'last':
        for levelnr in xrange(open_levelnr, len(levels)):
            level = levels[levelnr]
            result += '<' + level + ' code="' + src_fields[level] + '">\n'
    return result


def make_sentence(line, sent_nr, src_code, src_fields):
    return (u'<sentence id="{0}" code="{1}" page="{2}">\n'
            .format(sent_nr, src_code, src_fields['page'])
            + line.replace(' ', '\n')
            + '</sentence>\n')


def getopts():
    optparser = OptionParser()
    (opts, args) = optparser.parse_args()
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    process_input(sys.stdin)
    

if __name__ == "__main__":
    main()
