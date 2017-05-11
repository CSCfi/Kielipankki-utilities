#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Convert Mark Davies's corpora in word/lemma/PoS format to VRT.
"""

# TODO:
# - Add finer-grained datefrom, dateto based on possible date info in
#   the publication info or URL.
# - Extract more information (such as publication name, volume issue)
#   from the publication information field to separate attributes,
#   dependent on corpus and genre.
# - Check for unwanted characters, like special spaces.
# - Split the GloWbE metadata field "country genre" to separate
#   country and genre.


import re
import csv
import sys
import argparse
import os.path

from io import open
from xml.sax.saxutils import escape, unescape

import korpimport.xmlutil as xu


class WlpToVrtConverter:

    _attrname_map = {
        'textID': 'id',
        '#words': 'wordcount',
        '# words': 'wordcount',
        'subgen': 'subgenre',
        '': 'publ_info',          # For coca-sources.txt
        'Publication information': 'publ_info',
        '(publication info, for non-spoken)': '',  # Skip; for coca-sources.txt
        'Library of Congress Classification (NF)': 'lcc',
        'URL': 'url',
    }
    _progress_step = 1000000

    def __init__(self, args):
        self._filenames = args.filenames or []
        self._metadata = {}
        self._opts = args
        self._read_metadata_file(args.metadata_file)

    def _read_metadata_file(self, filename):
        with open(filename, 'r', encoding='cp1252') as metadatafile:
            reader = csv.DictReader(metadatafile, delimiter='\t',
                                    quoting=csv.QUOTE_NONE, restval='')
            for fields in reader:
                if fields['textID'] not in ['----', '']:
                    self._metadata[fields['textID']] = dict(
                        ((name, val.strip()) for name, val in fields.items()))
            self._attrnames = [
                (self._attrname_map.get(fieldname, fieldname)
                 .lower().replace(' ', '_'), fieldname)
                for fieldname in reader.fieldnames] + [
                        'filename', 'datefrom', 'dateto']

    def convert(self):
        for filename in self._filenames:
            with open(filename, 'r', encoding='cp1252') as f:
                self._convert_file(filename, f)

    def _convert_file(self, filename, f):
        lines = []
        text_id = None
        text_id_marker = None
        self._output_verbose(filename + ':')
        for linenr, line in enumerate(f):
            if self._opts.verbose and (linenr + 1) % self._progress_step == 0:
                self._output_verbose(
                    ' ' + str((linenr + 1) // self._progress_step))
            fields = line.strip('\n').split('\t')
            if len(fields) == 5:
                # Take the last three fields to skip the token number
                # and text id in the COCA addednum.
                fields = fields[-3:]
            elif len(fields) == 4 and fields[3] == '':
                # COHA sometimes has a trailing tab
                fields = fields[:3]
            # COHA files have lines with "q!" as the word, lemma and
            # PoS at the end of many files. It probably won't hurt to
            # remove them.
            if fields[0] == 'q!':
                continue
            # Check if the line contains a text id: some lines may
            # begin with a "##" without being text start lines, at
            # least in COHA.
            matchobj = None
            if text_id_marker is None:
                if fields[0].startswith('##') or fields[0].startswith('@@'):
                    text_id_marker = fields[0][:2]
                    matchobj = re.search(r'(\d+)', fields[0])
            elif fields[0].startswith(text_id_marker):
                matchobj = re.search(r'([1-9]\d*)', fields[0])
            if matchobj:
                if lines:
                    self._output_text(text_id, lines, filename, linenr)
                    lines = []
                text_id = matchobj.group(1)
            else:
                self._fix_lemma(fields)
                self._add_pos_set(fields)
                lines.append(fields)
        self._output_verbose(' ' + str(linenr + 1) + ' lines\n')
        if lines:
            self._output_text(text_id, lines, filename, linenr)

    def _fix_lemma(self, fields):
        # COHA sometimes has NULL in the lemma field
        if fields[1] == '\x00':
            fields[1] = fields[0]
        # GloWbE has an empty lemma for punctuation and the
        # punctuation mark as the PoS
        if (fields[1] == '' and fields[2] == fields[0]
            and (len(fields[0]) == 1 or fields[0] == '...')
            and not fields[0][0].isalnum()):
            fields[1] = fields[0]
            fields[2] = 'y'
        # Copy @ to lemma and add PoS GAP for omitted parts
        if fields[0] == '@' and fields[1] in ['', '\x00', '@']:
            fields[1] = '@'
            fields[2] = 'GAP'

    def _add_pos_set(self, fields):
        """Add a split, normalized PoS a feature set attribute

        Split PoS at underscores to different alternatives, strip
        trailing % and @ and strip the multi-word-expression markers
        (two trailing digits). Enclose and separate the resulting PoS
        by vertical bars and add it as the third field.
        """

        def get_base_pos(pos):
            return re.sub(r'[2-9]\d$', '', re.sub(r'(?<!")[@%]', '', pos))

        fields[2:2] = ['|' + '|'.join(get_base_pos(pos)
                                      for pos in fields[2].split('_')) + '|']

    def _output_text(self, text_id, lines, filename, linenr):
        attrs = self._metadata.get(text_id, {})
        filename_base = os.path.basename(filename)
        if not attrs:
            mo = re.search(r'_[12]\d{3}_(\d+)\.txt', filename_base)
            if mo:
                text_id = mo.group(1)
                attrs = self._metadata.get(text_id, {})
        if not attrs:
            self._warn('Metadata information not found for text id ' + text_id,
                       filename, linenr + 1)
        attrs['filename'] = filename_base
        self._add_dateinfo(attrs)
        self._output(xu.make_starttag('text', attrnames=self._attrnames,
                                      attrdict=attrs)
                     + '\n')
        lines = self._add_structs(lines)
        self._output(self._format_lines(lines))
        self._output('</text>\n')

    def _add_dateinfo(self, attrs):
        # TODO: Add month or date information whenever available in
        # publ_info or url
        if 'year' in attrs:
            attrs['datefrom'] = attrs['year'] + '0101'
            attrs['dateto'] = attrs['year'] + '1231'
        else:
            attrs['datefrom'] = attrs['dateto'] = ''

    def _add_structs(self, lines):
        para_tags = ['<p>', '<h>', '#']
        para_types = {'<p>': 'paragraph',
                      '<h>': 'heading',
                      '#': 'paragraph/heading'}
        result = []
        sent_start_para_type = (
            None if any(line[0] in ['<p>', '#'] for line in lines)
            else 'sentence')
        sent_start = 0
        next_sent_end = None
        line_count = len(lines)
        in_quote = None
        in_gap = False

        def add_start_tags(para_type=None):
            nonlocal sent_start
            if para_type:
                result.append(['<paragraph type="' + para_type + '">'])
            result.append(['<sentence gaps="no">'])
            sent_start = len(result) - 1

        def add_end_tags(para_type=None):
            nonlocal gaps
            result.append(['</sentence>'])
            if para_type:
                result.append(['</paragraph>'])
            if gaps:
                result[sent_start] = ['<sentence gaps="yes">']
                gaps = False

        def is_sent_start_word(line):
            """Check if the token is a likely sentence start word.

            Return 0 if the word does not begin with an upper-case
            letter, 1 if it begins with an upper-case letter but is or
            may be a proper noun, and 2 if it is not marked as a
            proper noun.
            """
            if not line[0][0].isupper():
                return 0
            elif not any(tag[:2] == 'np' for tag in line[3].split('_')):
                return 2
            else:
                return 1

        def is_quote(line):
            return (line[0] == '"' or line[3] == '"@')

        def is_closing_quote(line):
            return (is_quote(line) and in_quote == line[0])

        def is_sent_end(linenr, line):
            nonlocal next_sent_end, in_gap, result
            if next_sent_end is not None:
                if next_sent_end == linenr:
                    next_sent_end = None
                    return True
                else:
                    return False
            if linenr >= line_count - 1:
                return False
            line1 = lines[linenr + 1]
            if line[0] == '@' and is_sent_start_word(line1) == 2:
                in_gap = False
                result.append(['</gap>'])
                return True
            if (line1[0] in '#*' and linenr + 2 < line_count
                and (is_sent_start_word(lines[linenr + 2]) == 2
                     or (linenr + 3 < line_count
                         and is_sent_start_word(lines[linenr + 3]) == 2
                         and is_quote(lines[linenr + 2])))):
                return True
            if line[0] not in '...?!:':
                return False
            linenr1 = linenr + 1
            while linenr1 < line_count and (lines[linenr1][0] == ')'
                                            or is_quote(lines[linenr1])):
                linenr1 += 1
            if linenr1 == line_count:
                next_sent_end = linenr1 - 1
                return False
            elif (not is_sent_start_word(lines[linenr1])
                  and lines[linenr1][0] not in ['@', '(']):
                return False
            elif linenr1 == linenr + 1:
                return True
            next_sent_end = find_sent_end(linenr + 1, linenr1)
            if next_sent_end == linenr:
                next_sent_end = None
            return (next_sent_end is None)

        def find_sent_end(start, end):
            # Check the following punctuation ("e = end quote,
            # "s = start quote, A = capitalized word):
            # . ) <s> A | . "e <s> A | . <s> "s A |
            # . ) "e <s> A | . ) <s> "s A | . "e ) <s> A | . "s ) <s> A |
            # . ' "e <s> A | . ' "e ) <s> A | . "e <s> "s A
            # nonlocal next_sent_end
            closing_quote_seen = False
            linenr = start
            # TODO: Explain, what this does
            while (linenr < end
                   and (lines[linenr][0] == ')'
                        or (is_quote(lines[linenr])
                            and ((is_closing_quote(lines[linenr])
                                  and not closing_quote_seen)
                                 or (linenr + 1 < end
                                     and lines[linenr + 1][0] == ')'))))):
                if is_closing_quote(lines[linenr]):
                    closing_quote_seen = True
                linenr += 1
            return linenr - 1

        gaps = False
        for linenr, line in enumerate(lines):
            if line[0] in para_tags:
                if linenr < line_count - 1 and lines[linenr + 1] in para_tags:
                    # Only the last consecutive paragraph tag counts
                    continue
                para_type = para_types[line[0]]
                in_quote = None
                if linenr > 0:
                    add_end_tags(para_type)
                add_start_tags(para_type)
            else:
                if line[3] == 'GAP':
                    if not in_gap:
                        gaps = True
                        in_gap = True
                        result.append(['<gap>'])
                elif in_gap:
                    result.append(['</gap>'])
                    in_gap = False
                if linenr == 0:
                    # No <p> at the start of the text
                    add_start_tags(sent_start_para_type or 'paragraph')
                if is_quote(line):
                    if (in_quote == line[0]
                        or (linenr < line_count - 1
                            and lines[linenr + 1][0] == ')')):
                        # A quote that is immediately followed by a
                        # closing bracket is hardly an opening quote;
                        # it might be a closing quote, whose opening
                        # quote is replaced by a gap.
                        in_quote = None
                    else:
                        in_quote = line[0]
                result.append(line)
                if (linenr < line_count - 1
                    and lines[linenr + 1][0] not in para_tags
                    and is_sent_end(linenr, line)):
                    add_end_tags(sent_start_para_type)
                    add_start_tags(sent_start_para_type)
        add_end_tags('paragraph')
        return result

    def _add_paragraphs(self, lines):
        result = []
        for linenr, line in enumerate(lines):
            if line[0] == '<p>':
                if linenr > 0:
                    result.append(['</paragraph>'])
                result.append(['<paragraph>'])
            else:
                if linenr == 0:
                    # No <p> at the start of the text
                    result.append(['<paragraph>'])
                result.append(line)
        result.append(['</paragraph>'])
        return result

    def _format_lines(self, lines):

        def format_line(fields):
            if len(fields) == 1:
                return fields[0]
            else:
                return '\t'.join(format_field(field) for field in fields)

        def format_field(text):
            # First convert any existing &lt;, &gt; and &amp; to the
            # corresponding characters and then convert the characters
            # to the entities.
            # FIXME: This does not handle numeric or other character
            # entities.
            return escape(unescape(text.strip()))

        return '\n'.join(format_line(line) for line in lines) + '\n'

    def _output(self, text):
        sys.stdout.write(text)

    def _output_verbose(self, text):
        if self._opts.verbose:
            sys.stderr.write(text)
            sys.stderr.flush()

    def _warn(self, text, filename=None, linenr=None):
        msg = 'Warning ' + text
        if filename:
            msg += ' (' + filename
        if linenr is not None:
            if not filename:
                msg += '(' + '(stdin)'
            msg += ':' + str(linenr)
        if filename or linenr:
            msg += ')'
        msg += '\n'
        sys.stderr.write(msg)


def getargs():
    argparser = argparse.ArgumentParser(
        description='''Convert Mark Davies's corpora in WLP format to VRT''')
    argparser.add_argument('filenames', nargs='*',
                           help='names of input files in word/lemma/PoS format')
    argparser.add_argument('--metadata-file', metavar='FILE', required=True,
                           help='read text metadata from FILE in TSV format')
    argparser.add_argument('--verbose', action='store_true',
                           help='output progess information to stderr')
    return argparser.parse_args()


def main():
    args = getargs()
    converter = WlpToVrtConverter(args)
    converter.convert()


if __name__ == '__main__':
    main()
