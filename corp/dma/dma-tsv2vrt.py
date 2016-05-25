#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
Convert DMA (Digital Morphology Archive) TSV data to VRT

The input TSV data is a dump of the DMA MySQL table.
"""

# TODO:
# - Align the text and search fields when they have a different number
#   of tokens
# - Possibly add search words with replacement characters removed or
#   converted to those sentences lacking them.


import sys
import re
import time

from xml.sax.saxutils import escape

import korpimport.util


class DmaToVrtConverter(korpimport.util.InputProcessor):

    def __init__(self, args=None):
        super(DmaToVrtConverter, self).__init__()
        self._linenr = 0
        self._fieldnames = {}
        self._empty_count = 0
        self._mismatch_count = 0
        self._empty_text_count = 0
        self._dupl_count = 0
        self._timestamp = str(int(time.time()))
        self._seen_clauses = {}

    def process_input_stream(self, stream, filename=None):
        for linenr, line in enumerate(stream):
            if linenr == 0:
                self._fieldnames = line[:-1].split('\t')
            else:
                self._linenr = linenr + 1
                converted_line = self._convert_line(line)
                if converted_line:
                    sys.stdout.write(converted_line)
        for count, descr in [
                (self._empty_count, 'sentences with one empty sequence'),
                (self._mismatch_count, 'sentence token count mismatches'),
                (self._empty_text_count, 'sentences with empty text'),
                (self._dupl_count, 'duplicate sentences'),]:
            if count > 0:
                sys.stderr.write('Warning: {0} {1}\n'.format(count, descr))

    def _convert_line(self, line):
        fields = self._make_fields(line[:-1].split('\t'))
        if fields['text'] in ['-', '']:
            sys.stderr.write(u'Warning: skipping line {0} with empty text:\n{1}'
                             .format(self._linenr, line))
            self._empty_text_count += 1
            return ''
        if (fields['parish'], fields['text']) in self._seen_clauses:
            dupl_linenr, dupl_line = self._seen_clauses[(fields['parish'],
                                                         fields['text'])]
            sys.stderr.write(
                u'Warning: skipping line {0} as duplicate of {1}:\n'
                u'  {0}:\t{2}  {1}:\t{3}'
                .format(self._linenr, dupl_linenr, line, dupl_line))
            self._dupl_count += 1
            return ''
        self._seen_clauses[(fields['parish'], fields['text'])] = (self._linenr,
                                                                  line)
        fields['signumlist'] = fields['signum']
        fields['signum'] = '|' + '|'.join(fields['signum'].split()) + '|'
        # sys.stderr.write(repr(fields) + '\n')
        fields['informant_sex'], fields['informant_birthyear'] = (
            self._extract_informant_info(fields['informant']))
        fields['parish_name'], fields['village'] = self._split_village(
            fields['parishname'])
        for field in ['text', 'search']:
            fields[field + '_words'] = self._make_words_featset(fields[field])
        if fields['search_words'] == '||':
            fields['search_words'] = fields['text_words']
        fields['dialect_group'] = fields['area']
        fields['dialect_region'] = fields['dialect_group'][0]
        fields['word_type'] = self._make_word_types(fields['text'])
        # Should we convert a single dash to an empty value in other
        # fields as well?
        if fields['pdf'] == '-':
            fields['pdf'] = ''
        if not fields['updated']:
            fields['updated'] = self._timestamp
        result = []
        result.append(self._make_start_tag(
            'text', fields, ['dialect_region', 'dialect_group',
                             'parish', 'parish_name', 'village']))
        result.append(self._make_start_tag(
            'sentence', fields,
            ['id', 'signum', 'signumlist', 'informant', 'informant_sex',
             'informant_birthyear', 'comment', 'location', 'pdf', 'updated',
             'text_words', 'search_words']))
        result.extend(self._verticalize(fields['text'], fields['search'],
                                        fields['word_type']))
        result.append('</sentence>')
        result.append('</text>')
        return '\n'.join(result) + '\n'
    
    def _make_fields(self, values):
        d = dict((self._fieldnames[num].lower(), val)
                 for num, val in enumerate(values))
        # print values, d
        return d

    def _extract_informant_info(self, informant):
        sex = birthyear = ''
        if len(informant) > 0 and informant[0] in 'mn':
            sex = informant[0]
        if len(informant) > 4:
            try:
                birthyear_val = int(informant[1:5])
                if 1800 <= birthyear_val <= 2000:
                    birthyear = str(birthyear_val)
            except ValueError:
                pass
        return sex, birthyear

    def _split_village(self, parish_name):
        mo = re.match(r'(.*?) \((.*?)\)', parish_name)
        if mo:
            return mo.group(1), mo.group(2)
        else:
            return parish_name, ''

    def _make_word_types(self, text):
        word_types = []
        comment = False
        for word in text.split():
            if word == '[':
                comment = True
            word_types.append('comment' if comment else 'informant')
            if word == ']':
                comment = False
        return ' '.join(word_types)

    def _make_words_featset(self, text):
        return ('|'
                + '|'.join(word for word in
                           sorted(set(text.replace('|', u'\x83').split()))
                           if word != '|')
                + '|')

    def _make_start_tag(self, elemname, attrdict, attrs):
        return ('<' + elemname + ' '
                + ' '.join((name + '="'
                            + escape(attrdict[name], {'"': '&quot;'}) + '"')
                           for name in attrs)
                + '>')

    def _verticalize(self, *fields):
        tokenfields = [field.split() for field in fields]
        result = []
        tokenfield_lens = [len(tokenfield) for tokenfield in tokenfields]
        min_tokencount = min(tokenfield_lens)
        max_tokencount = max(tokenfield_lens)
        # print fields, tokenfields, tokenfield_lens, min_tokencount, max_tokencount
        if min_tokencount != max_tokencount:
            if min_tokencount == 0:
                empty_tokenfields = [
                    i for i, tflen in enumerate(tokenfield_lens) if tflen == 0]
                maxlen_tokenfield = tokenfield_lens.index(max_tokencount)
                # print empty_tokenfields, maxlen_tokenfield
                for empty_tf in empty_tokenfields:
                    tokenfields[empty_tf] = tokenfields[maxlen_tokenfield]
                self._empty_count += 1
                # print tokenfields
            else:
                sys.stderr.write(
                    u'Warning: token counts differ on line {0}: {1!r}: {2!r}\n'
                    .format(self._linenr, tokenfield_lens, fields))
                self._mismatch_count += 1
                tokenfields = self._justify(tokenfields)
        for i in xrange(max_tokencount):
            result.append(
                '\t'.join(escape(korpimport.util.elem_at(tokenfield, i,
                                                         tokenfields[0][i])
                                 .replace(r'\\', '\\'))
                          for tokenfield in tokenfields))
        return result

    def _justify(self, tokenlists):
        # print 'J1', tokenlists
        maxlen = max(len(tokenlist) for tokenlist in tokenlists)
        for i in xrange(len(tokenlists)):
            tl_len = len(tokenlists[i])
            if tl_len < maxlen:
                # print 'EXTEND'
                tokenlists[i].extend((maxlen - tl_len) * [''])
        # print 'J2', tokenlists
        return tokenlists


if __name__ == "__main__":
    DmaToVrtConverter().run()
