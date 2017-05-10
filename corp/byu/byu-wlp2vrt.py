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
# - Check the handling of sentence boundaries at quotes and brackets.
# - Check for unwanted characters, like special spaces.
# - Split the GloWbE metadata field "country genre" in to separate
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

    def __init__(self, args):
        self._filenames = args.filenames or []
        self._metadata = {}
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
        for linenr, line in enumerate(f):
            fields = line.strip('\n').split('\t')
            if len(fields) == 5:
                # Take the last three fields to skip the token number
                # and text id in the COCA addednum.
                fields = fields[-3:]
            elif len(fields) == 4 and fields[3] == '':
                # COHA sometimes has a trailing tab
                fields = fields[:3]
            if fields[0].startswith('##') or fields[0].startswith('@@'):
                if lines:
                    self._output_text(text_id, lines, filename, linenr)
                    lines = []
                matchobj = re.search(r'(\d+)', fields[0])
                text_id = matchobj.group(1) if matchobj else None
            else:
                self._fix_lemma(fields)
                self._add_pos_set(fields)
                lines.append(fields)
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
        attrs['filename'] = os.path.basename(filename)
        if not attrs:
            self._warn('Metadata information not found for text id ' + text_id,
                       filename, linenr + 1)
        # print(attrs, self._metadata_fieldnames)
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
        para_tags = ['<p>', '<h>']
        para_types = {'<p>': 'paragraph', '<h>': 'heading'}
        result = []
        sent_start_para_type = (
            None if any(line[0] == '<p>' for line in lines) else 'sentence')
        sent_start = 0

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

        end_after_next = False
        gaps = False
        for linenr, line in enumerate(lines):
            if line[0] in para_tags:
                para_type = para_types[line[0]]
                if linenr > 0:
                    add_end_tags(para_type)
                add_start_tags(para_type)
            else:
                if line[0] == '@':
                    gaps = True
                if linenr == 0:
                    # No <p> at the start of the text
                    add_start_tags(sent_start_para_type or 'paragraph')
                result.append(line)
                if linenr < len(lines) - 1:
                    if end_after_next:
                        if lines[linenr + 1] not in para_tags:
                            add_end_tags(sent_start_para_type)
                            add_start_tags(sent_start_para_type)
                        end_after_next = False
                    if line[0] in '.?!:':
                        if lines[linenr + 1][0][0] in '"”)]':
                            if (line[0] == '.'
                                or (linenr < len(lines) - 2
                                    and lines[linenr + 2][0][0].isupper())):
                                end_after_next = True
                        elif ((line[0] == '.'
                               or lines[linenr + 1][0][0].isupper())
                              and lines[linenr + 1][0] not in para_tags):
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
    return argparser.parse_args()


def main():
    args = getargs()
    converter = WlpToVrtConverter(args)
    converter.convert()


if __name__ == '__main__':
    main()
