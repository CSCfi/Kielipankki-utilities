#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import re

import korpimport.util
import korpimport.xmlutil as xmlutil


class NameAttrConverter(korpimport.util.InputProcessor):

    def __init__(self, args=None):
        super(NameAttrConverter, self).__init__()
        self._name_endtag = '</' + self._opts.name_struct + '>\n'

    def process_input_stream(self, stream, filename=None):
        self._filename = filename
        name_type = None
        name_tokens = []
        for linenr, line in enumerate(stream):
            self._linenr = linenr + 1
            bio = None
            if line[0] == '<':
                if self._opts.output_input_structs:
                    self.output(line)
            else:
                fields = line[:-1].split('\t')
                nertag = self._get_ner_tag(fields, name_type)
                if nertag:
                    if name_type:
                        if nertag[0] != '/':
                            self.warn(u'name {0} within name {1}'
                                      .format(nertag, name_type))
                        else:
                            if nertag[1:] != name_type:
                                self.warn(u'NER tag mismatch: {0} closed by {1}'
                                          .format(name_type, nertag[1:]))
                            if self._opts.add_bio_attribute:
                                fields.append('I')
                            name_tokens.append(fields)
                            self._output_name(name_type, name_tokens)
                            name_type = None
                            name_tokens = []
                            continue
                    elif nertag[-1] == '/':
                        if self._opts.add_bio_attribute:
                            fields.append('B')
                        self._output_name(nertag[:-1], [fields])
                        continue
                    else:
                        if nertag[0] == '/':
                            self.warn(u'ignoring lone NER end tag ' + nertag)
                        else:
                            name_type = nertag
                            bio = 'B'
                if name_type:
                    if self._opts.add_bio_attribute:
                        fields.append(bio or 'I')
                    name_tokens.append(fields)
                else:
                    if self._opts.add_bio_attribute:
                        fields.append('O')
                    self._output_fields(fields)
        if name_tokens:
            self.warn('unclosed NER tag ' + name_type + ' at the end of file')
            for token in name_tokens:
                self._output_fields(token)

    def _get_ner_tag(self, fields, name_type):
        try:
            nertag = fields[self._opts.nertag_field]
            if nertag == '' or nertag == '_':
                return None
            if '&gt;&lt;' in nertag:
                # Multiple tags
                nertags = nertag.split('&gt;&lt;')
                if name_type:
                    # If inside a name, close it if a the tags contain
                    # a corresponding end tag
                    for tag in nertags:
                        if tag[1:] == name_type:
                            self.warn(u'ignoring alternative NER end tag '
                                      + ' '.join(tag1 for tag1 in nertags
                                                 if tag1 != tag))
                            return tag
                    self.warn(u'ignoring mismatched NER end tags for {0}: {1}'
                              .format(name_type,' '.join(nertags)))
                    return None
                else:
                    start_tags = [tag for tag in nertags
                                  if tag[0] != '/' and tag[-1] != '/']
                    if start_tags:
                        if len(start_tags) > 1:
                            self.warn('ignoring alternative NER start tag '
                                      + start_tags[1])
                        return start_tags[0]
                    empty_tags = [tag for tag in nertags if tag[-1] == '/']
                    if empty_tags:
                        if len(empty_tags) > 1:
                            self.warn('ignoring alternative NER empty tag '
                                      + empty_tags[1])
                        return empty_tags[0]
            else:
                return nertag
        except IndexError:
            return None

    def _output_name(self, name_type, name_tokens):
        self.output(self._make_name_starttag(name_type, name_tokens) + '\n')
        for token_fields in name_tokens:
            self._output_fields(token_fields)
        self.output(self._name_endtag)

    def _make_name_starttag(self, name_type, name_tokens):
        mo = re.search(r'((?:Ena|Nu|Ti)mex)(...)(...)', name_type)
        attrs = []
        name = self._make_name(name_tokens, mo.group(1))
        attrs.append(('name', name))
        attrs.append(('fulltype', name_type))
        for group, attrname in enumerate(['ex', 'type', 'subtype']):
            attrs.append((attrname, mo.group(group + 1).upper()))
        is_placename = mo.group(2) == 'Loc'
        attrs.append(('placename', name if is_placename else ''))
        attrs.append(('placename_source', 'ner' if is_placename else ''))
        return xmlutil.make_starttag(self._opts.name_struct, attrs=attrs)
        
    def _make_name(self, name_tokens, name_cat):
        if name_cat in ['Timex', 'Numex']:
            return ' '.join(
                token[self._opts.word_field] for token in name_tokens)
        else:
            last_wordform = name_tokens[-1][self._opts.word_field]
            last_lemma = name_tokens[-1][self._opts.lemma_field]
            if last_wordform.istitle():
                last_lemma = last_lemma.title()
            elif last_wordform.isupper():
                last_lemma = last_lemma.upper()
            return ' '.join([token[self._opts.word_field]
                             for token in name_tokens[:-1]]
                            + [last_lemma])

    def _output_fields(self, fields):
        if not self._opts.output_fields:
            self.output('\n')
        else:
            # sys.stderr.write(repr(self._linenr) + ' ' + repr(fields) + '\n')
            self.output(
                '\t'.join(fields[fieldnr]
                          for fieldnr in self._opts.output_fields)
                + '\n')
 
    def getopts(self, args=None):
        self.getopts_basic(
            dict(usage="%progname [options] [input] > output",
                 description=(
"""Add named entity (NE) tags (structural attributes) to VRT input based on
positional attributes containing Pmatch-style NER tags, word form and base
form.
""")
             ),
            args,
            ['--word-field', '--wordform-field', dict(
                type='int',
                default=1,
                metavar='FIELDNR',
                help=('field number FIELDNR contains word form'
                      ' (default: %default)'))],
            ['--lemma-field', '--baseform-field', dict(
                type='int',
                default=2,
                metavar='FIELDNR',
                help=('field number FIELDNR contains base form'
                      ' (default: %default)'))],
            ['--nertag-field', dict(
                type='int',
                default=3,
                metavar='FIELDNR',
                help=('field number FIELDNR contains NER tags'
                      ' (default: %default)'))],
            ['--output-fields', dict(
                default='1',
                metavar='FIELDNRLIST',
                help=('output fields whose numbers are listed in FIELDNRLIST,'
                      ' separated by commas or spaces (default: %default)'))],
            ['--name-struct', '--ne-struct', dict(
                default='ne',
                metavar='STRUCTNAME',
                help=('add name information to structural attributes named'
                      ' STRUCTNAME (default: %default)'))],
            ['--output-input-structs', dict(
                action='store_true',
                help=('output structural attributes (tags) in the input',
                      ' (default: do not output)'))],
            ['--add-bio-attribute', dict(
                action='store_true',
                help=('add a positional attribute containing the B-I-O'
                      ' information of a word'))],
        )
        self._opts.word_field -= 1
        self._opts.lemma_field -= 1
        self._opts.nertag_field -= 1
        if self._opts.output_fields:
            self._opts.output_fields = [
                int(fieldnr) - 1
                for fieldnr in re.split(r'[,\s]\s*', self._opts.output_fields)]
        else:
            self._opts.output_fields = []
        if self._opts.add_bio_attribute:
            self._opts.output_fields.append(-1)


if __name__ == "__main__":
    NameAttrConverter().run()
