#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

from optparse import OptionParser


def replace_substrings(s, mapping):
    """Replace substrings in s according to mapping (a sequence of
    pairs (string, replacement): replace each string with the
    corresponding replacement.
    """
    for (s1, repl) in mapping:
        s = s.replace(s1, repl)
    return s


class AttributeFixer(object):

    def __init__(self, opts):
        self._opts = opts
        if self._opts.angle_brackets:
            self._opts.angle_brackets = self._opts.angle_brackets.split(',', 1)
        self._split_lines = (self._opts.compound_boundaries != 'keep'
                             or self._opts.strip
                             or self._opts.empty_field_values
                             or self._opts.missing_field_values)
        self._encode_posattrs = (self._opts.encode_special_chars
                                 in ['all', 'pos'])
        self._encode_structattrs = (self._opts.encode_special_chars
                                    in ['all', 'struct'])
        self._special_char_encode_map = [
            (c, (opts.encoded_special_char_prefix
                 + unichr(i + opts.encoded_special_char_offset)))
            for (i, c) in enumerate(opts.special_chars)]
        self._empty_field_values = self._make_default_field_values(
            self._opts.empty_field_values)
        self._missing_field_values = self._make_default_field_values(
            self._opts.missing_field_values)
        if self._missing_field_values:
            self._max_fieldnum = max(self._missing_field_values.keys())
        else:
            self._max_fieldnum = -1
        self._elem_renames = {}
        self._elem_ids = {}
        for rename_elem_str in self._opts.rename_element:
            for rename_spec in re.split(r'\s*[,\s]\s*', rename_elem_str):
                oldname, newname = rename_spec.split(':')
                self._elem_renames[oldname] = newname
        for elemnames_str in self._opts.add_element_id:
            elemnames = re.split(r'\s*[,\s]\s*', elemnames_str)
            for elemname in elemnames:
                self._elem_ids[elemname] = 0

    def _make_default_field_values(self, fieldspec):
        if not fieldspec:
            return {}
        fieldvals_list = re.split(r'\s*;\s*', fieldspec)
        fieldval_fns = {}
        for field_numval in fieldvals_list:
            (fieldnumstr, fieldval) = re.split(r'\s*:\s*', field_numval)
            fieldnums = self._extract_fieldnums(fieldnumstr)
            if re.match(r'\$\d+', fieldval):
                fieldval = int(fieldval[1:]) - 1
                fieldval_fn = \
                    lambda attrs, val=fieldval: (attrs[val] if val < len(attrs)
                                                 else '')
            else:
                fieldval_fn = lambda attrs, val=fieldval: val
            for fieldnum in fieldnums:
                fieldval_fns[fieldnum] = fieldval_fn
        return fieldval_fns

    def _extract_fieldnums(self, fieldnumstr):
        result = []
        for fieldrange in re.split(r'\s*,\s*', fieldnumstr):
            if fieldrange == '*':
                result.append(-1)
            else:
                if '-' in fieldrange:
                    (start, end) = fieldrange.split('-', 1)
                else:
                    start = end = fieldrange
                result.extend(range(int(start) - 1, int(end)))
        return result

    def process_files(self, files):
        if isinstance(files, list):
            for file_ in files:
                self.process_files(file_)
        elif isinstance(files, basestring):
            with codecs.open(files, 'r', encoding='utf-8') as f:
                self._fix_input(f)
        else:
            self._fix_input(files)

    def _fix_input(self, f):
        for line in f:
            sys.stdout.write(self._make_fixed_line(line))

    def _make_fixed_line(self, line):
        if line.startswith('<') and line.endswith('>\n'):
            line = self._fix_structattrs(line)
            if self._encode_structattrs:
                return self._encode_special_chars_in_struct_attrs(line)
            else:
                return line
        else:
            return self._fix_posattrs(line)

    def _fix_posattrs(self, line):
        if self._split_lines:
            attrs = line[:-1].split('\t')
            self._process_compound_lemmas(attrs)
            self._strip_attrs(attrs)
            if self._empty_field_values or self._missing_field_values:
                self._add_default_field_values(attrs)
            line = '\t'.join(attrs) + '\n'
        if self._opts.space:
            line = line.replace(' ', self._opts.space)
        if self._opts.angle_brackets:
            line = (line.replace('<', self._opts.angle_brackets[0])
                    .replace('>', self._opts.angle_brackets[1]))
        if self._encode_posattrs:
            line = self._encode_special_chars(line)
        return line

    def _encode_special_chars(self, s):
        """Encode the special characters in s."""
        return replace_substrings(s, self._special_char_encode_map)

    def _encode_special_chars_in_struct_attrs(self, s):
        """Encode the special characters in the double-quoted substrings
        of s.
        """
        return re.sub(r'("(?:[^\\"]|\\[\\"])*")',
                      lambda mo: self._encode_special_chars(mo.group(0)), s)

    def _process_compound_lemmas(self, attrs):
        if self._opts.compound_boundaries != 'keep':
            noncompound_lemma = attrs[self._opts.lemma_field] .replace('#', '')
            if self._opts.compound_boundaries == 'remove':
                attrs[self._opts.lemma_field] = noncompound_lemma
            elif self._opts.compound_boundaries == 'new':
                attrs.insert(self._opts.noncompound_lemma_field,
                             noncompound_lemma)

    def _strip_attrs(self, attrs):
        if self._opts.strip:
            for attrnr in xrange(0, len(attrs)):
                attrs[attrnr] = attrs[attrnr].strip()

    def _add_default_field_values(self, attrs):
        if self._empty_field_values:
            for (attrnum, attr) in enumerate(attrs):
                if attr == '' and (attrnum in self._empty_field_values
                                   or -1 in self._empty_field_values):
                    attrs[attrnum] = self._empty_field_values.get(
                        attrnum, self._empty_field_values.get(
                            -1, lambda x: ''))(attrs)
        orig_attrcount = len(attrs)
        if self._missing_field_values and orig_attrcount < self._max_fieldnum:
            for attrnum in xrange(orig_attrcount, self._max_fieldnum + 1):
                if (attrnum in self._missing_field_values
                    or -1 in self._empty_field_values):
                    attrval = self._missing_field_values.get(
                        attrnum, self._missing_field_values.get(
                            -1, lambda x: ''))(attrs)
                else:
                    attrval = ''
                attrs.append(attrval)

    def _fix_structattrs(self, line):
        if self._elem_renames:
            line = self._rename_elem(line)
        if self._elem_ids and not line.startswith('</'):
            line = self._add_elem_id(line)
        return line

    def _rename_elem(self, line):

        def rename_elem(matchobj):
            name = matchobj.group(2)
            return matchobj.group(1) + (self._elem_renames.get(name) or name)

        return re.sub(r'(</?)(\w+)', rename_elem, line)

    def _add_elem_id(self, line):
        elemname = re.search(r'(\w+)', line).group(1)
        if elemname in self._elem_ids:
            self._elem_ids[elemname] += 1
            line = (line[:-2] + ' id="{0:d}"'.format(self._elem_ids[elemname])
                    + line[-2:])
        return line


def getopts():
    optparser = OptionParser()
    optparser.add_option('--space', '--space-replacement', default=None)
    optparser.add_option('--no-strip', action='store_false', dest='strip',
                         default=True)
    optparser.add_option('--angle-brackets', '--angle-bracket-replacement',
                         default=None)
    optparser.add_option('--compound-boundaries', '--lemma-compound-boundaries',
                         type='choice', choices=['keep', 'remove', 'new'],
                         default='keep')
    optparser.add_option('--lemma-field', type='int', default=2)
    optparser.add_option('--noncompound-lemma-field', '--noncompound-field',
                         '--removed-compound-boundary-field', type='int',
                         default=None)
    optparser.add_option('--encode-special-chars', type='choice',
                         choices=['none', 'all', 'pos', 'struct'],
                         default='none')
    optparser.add_option('--special-chars', default=u' /<>|')
    optparser.add_option('--encoded-special-char-offset',
                         '--special-char-offset', default='0x7F')
    optparser.add_option('--encoded-special-char-prefix',
                         '--special-char-prefix', default=u'')
    optparser.add_option('--empty-field-values')
    optparser.add_option('--missing-field-values')
    optparser.add_option('--rename-element', action='append', default=[])
    optparser.add_option('--add-element-id', '--add-elem-id', action='append',
                         default=[])
    (opts, args) = optparser.parse_args()
    if opts.noncompound_lemma_field is None:
        opts.noncompound_lemma_field = opts.lemma_field
    opts.lemma_field -= 1
    opts.noncompound_lemma_field -= 1
    if opts.space == '':
        opts.space = ':'
    if opts.angle_brackets == '':
        opts.angle_brackets = '[,]'
    opts.encoded_special_char_offset = int(opts.encoded_special_char_offset,
                                           base=0)
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    attr_fixer = AttributeFixer(opts)
    attr_fixer.process_files(args if args else sys.stdin)


if __name__ == "__main__":
    main()
