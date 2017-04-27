#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Convert Mark Davies's corpora in word/lemma/PoS format to VRT.
"""


import re
import csv
import sys
import argparse
import os.path

from io import open

import korpimport.xmlutil as xu


class WlpToVrtConverter:

    _attrname_map = {
        'textID': 'id',
        '#words': 'wordcount',
        '# words': 'wordcount',
        'subgen': 'subgenre',
        '': 'publ_info',          # For coca-sources.txt
        'Publication information': 'publ_info',
        '(publication info, for non-spoken)': None,
        'Library of Congress Classification (NF)': 'lcc',
        'URL': 'url',
    }

    def __init__(self, args):
        self._filenames = args.filenames or []
        self._metadata = {}
        self._read_metadata_file(args.metadata_file)

    def _read_metadata_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as metadatafile:
            reader = csv.DictReader(metadatafile, delimiter='\t',
                                    quoting=csv.QUOTE_NONE, restval='')
            for fields in reader:
                if fields['textID'] not in ['----', '']:
                    self._metadata[fields['textID']] = dict(
                        ((name, val.strip()) for name, val in fields.items()))
            self._attrnames = [
                (self._attrname_map.get(fieldname, fieldname), fieldname)
                for fieldname in reader.fieldnames] + ['filename']

    def convert(self):
        for filename in self._filenames:
            with open(filename, 'r', encoding='utf-8') as f:
                self._convert_file(filename, f)

    def _convert_file(self, filename, f):
        lines = []
        text_id = None
        for linenr, line in enumerate(f):
            if line.startswith('##') or line.startswith('@@'):
                if lines:
                    self._output_text(text_id, lines, filename, linenr)
                    lines = []
                matchobj = re.search(r'(\d+)', line)
                text_id = matchobj.group(1) if matchobj else None
            else:
                # Take the last three fields to skip the token number
                # and text id in the COCA addednum.
                lines.append(line.strip().split('\t')[-3:])
        if lines:
            self._output_text(text_id, lines, filename, linenr)

    def _output_text(self, text_id, lines, filename, linenr):
        attrs = self._metadata.get(text_id, {})
        attrs['filename'] = os.path.basename(filename)
        if not attrs:
            self._warn('Metadata information not found for text id ' + text_id,
                       filename, linenr + 1)
        # print(attrs, self._metadata_fieldnames)
        self._output(xu.make_starttag('text', attrnames=self._attrnames,
                                      attrdict=attrs)
                     + '\n')
        lines = self._add_structs(lines)
        self._output(self._format_lines(lines))
        self._output('</text>\n')

    def _add_structs(self, lines):
        has_para_tags = any(line[0] == '<p>' for line in lines)
        lines = self._add_sentences(lines, not has_para_tags)
        if has_para_tags:
            lines = self._add_paragraphs(lines)
        return lines

    def _add_sentences(self, lines, sent_as_para=False):
        result = []

        def add_start_tags():
            if sent_as_para:
                result.append(['<paragraph>'])
            result.append(['<sentence>'])

        def add_end_tags():
            result.append(['</sentence>'])
            if sent_as_para:
                result.append(['</paragraph>'])

        add_start_tags()
        end_after_next = False
        for linenr, line in enumerate(lines):
            result.append(line)
            if linenr < len(lines) - 1:
                if end_after_next:
                    add_end_tags()
                    add_start_tags()
                    end_after_next = False
                if line[0] in '.?!:':
                    if lines[linenr + 1][0][0] in '"”)]':
                        if (line[0] == '.'
                            or (linenr < len(lines) - 2
                                and lines[linenr + 2][0][0].isupper())):
                            end_after_next = True
                    elif line[0] == '.' or lines[linenr + 1][0][0].isupper():
                        add_end_tags()
                        add_start_tags()
        add_end_tags()
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
        return '\n'.join('\t'.join(fields) for fields in lines) + '\n'

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
