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


def value_or_default(value, default):
    return value if value is not None else default


class PosAttrConverter(object):

    class OutputFieldSpec(object):

        def __init__(self, fieldspec, input_field_nums=None):
            self._input_field_nums = input_field_nums or {}
            self._opts = {}
            self._parse_fieldspec(fieldspec)

        def _parse_fieldspec(self, fieldspec):
            if ':' in fieldspec:
                name, opts = re.split(r':\s*', fieldspec, 1)
            else:
                name, opts = fieldspec, ''
            self._input_fieldnum = self._input_field_nums.get(name)
            # print fieldspec, name, opts, self._input_fieldnum
            if self._input_fieldnum is None:
                self._input_fieldnum = int(name) - 1
            for (key, val) in re.findall(
                r'(\w+)(?:=((?:[^,\'\"]|\'[^\']+\'|"[^\"]+")+))?', opts):
                self.set_option(key, self._remove_quotes(val))

        def _remove_quotes(self, value):
            return re.sub(r'"[^\"]+"|\'[^\']+\'', lambda mo: mo.group(0)[1:-1],
                          value)

        def set_option(self, key, value, override=False):
            if override and key in self._opts:
                return
            if key in ['missing', 'empty']:
                if re.match(r'\$\d+', value):
                    value = lambda attrs, val=value: attrs[int(val[1:]) - 1]
                elif re.match(r'\$\w+', value):
                    value = lambda attrs, val=value: \
                        attrs[self._input_field_nums.get(val[1:])]
                else:
                    value = lambda attrs, val=value: val
            self._opts[key] = value

        def make_field(self, input_fields, input_fieldnum=None):
            result = None
            if input_fieldnum is None:
                input_fieldnum = self._input_fieldnum
            if input_fieldnum >= len(input_fields):
                result = self._opts.get('missing', lambda s: None)(input_fields)
            else:
                result = (input_fields[input_fieldnum]
                          or self._opts.get('empty',
                                            lambda s: '')(input_fields))
            if result is not None:
                if 'noboundaries' in self._opts:
                    result = result.replace('#', '')
            return result

        def get_input_fieldnum(self):
            return self._input_fieldnum

        def __repr__(self):
            return str(self._input_fieldnum) + ':' + repr(self._opts)

    def __init__(self, input_fields, output_fields, strip=False,
                 empty_values=None, missing_values=None,
                 copy_extra_fields=None):
        self._make_input_fields(input_fields)
        self._copy_extra_fields = value_or_default(copy_extra_fields,
                                                   not output_fields)
        self._empty_field_values = self._make_default_field_values(empty_values)
        self._missing_field_values = self._make_default_field_values(
            missing_values)
        self._make_output_fields(output_fields)
        output_field_fieldnums = [output_field.get_input_fieldnum()
                                  for output_field in self._output_fields]
        self._max_fieldnum = max((output_field_fieldnums
                                  + self._empty_field_values.keys()
                                  + self._missing_field_values.keys())
                                 or [-1])
        # print self._output_fields, output_field_fieldnums, self._max_fieldnum
        for num in xrange(max(output_field_fieldnums or [-1]) + 1,
                          self._max_fieldnum + 1):
            self._output_fields.append(
                self.OutputFieldSpec(str(num + 1), self._input_fields))
        for type_, values in [('empty', self._empty_field_values),
                              ('missing', self._missing_field_values)]:
            self._add_default_fieldvals(type_, values)
        # print self._output_fields
        self._strip = strip

    def _make_input_fields(self, fields):
        if fields:
            fields = ' '.join(fields)
            self._input_fields = dict(
                [(name, num)
                 for num, name in enumerate(fields.strip().split())])
        else:
            self._input_fields = {}

    def _make_default_field_values(self, fieldspec):
        if not fieldspec:
            return {}
        fieldvals_list = re.split(r'\s*;\s*', fieldspec)
        fieldvals = {}
        for field_numval in fieldvals_list:
            (fieldnumstr, fieldval) = re.split(r'\s*:\s*', field_numval)
            fieldnums = self._extract_fieldnums(fieldnumstr)
            for fieldnum in fieldnums:
                fieldvals[fieldnum] = fieldval
        return fieldvals

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
                start = self._get_fieldnum(start)
                end = self._get_fieldnum(end)
                result.extend(range(start, end + 1))
        return result

    def _get_fieldnum(self, num_or_name):
        if re.match(r'^\d+$', num_or_name):
            return int(num_or_name) - 1
        else:
            return self._input_fields.get(num_or_name)

    def _make_output_fields(self, output_fieldslist):
        self._output_fields = []
        if output_fieldslist:
            for fields in output_fieldslist:
                fieldspecs = re.findall(r'(?:\S|\'[^\']+\'|"[^\"]+")+', fields)
                # print repr(fieldspecs)
                for fieldspec in fieldspecs:
                    self._output_fields.append(
                        self.OutputFieldSpec(fieldspec, self._input_fields))
        self._extra_output_field = self.OutputFieldSpec('0', self._input_fields)

    def _add_default_fieldvals(self, type_, values):
        for fieldnum, fieldval in values.items():
            if fieldnum != -1 and fieldnum <= self._max_fieldnum:
                self._output_fields[fieldnum].set_option(type_, fieldval)
        if -1 in values:
            for field in self._output_fields + [self._extra_output_field]:
                field.set_option(type_, values[-1], override=True)

    def convert_line(self, line, fieldsep='\t'):
        return fieldsep.join(self.convert(line.strip().split(fieldsep)))

    def convert(self, fields):
        outfields = []

        def add_output_field(fields, outfield_spec, fieldnum=None):
            outfield = outfield_spec.make_field(fields, fieldnum)
            if outfield is not None:
                outfields.append(outfield)

        # print fields, self._output_fields, self._copy_extra_fields
        if self._strip:
            fields = [field.strip() for field in fields]
        for output_field in self._output_fields:
            add_output_field(fields, output_field)
        if self._copy_extra_fields:
            for fieldnum in xrange(self._max_fieldnum + 1, len(fields)):
                add_output_field(fields, self._extra_output_field, fieldnum)
        return outfields


class AttributeFixer(object):

    _xml_char_entities = {'quot': '"',
                          'amp': '&',
                          'apos': '\'',
                          'lt': '<',
                          'gt': '>'}
    _xml_char_entity_name_regex = \
        r'#x[0-9a-fA-F]+|#[0-9]+|' + '|'.join(_xml_char_entities.keys())

    def __init__(self, opts):
        self._opts = opts
        if self._opts.angle_brackets:
            self._opts.angle_brackets = self._opts.angle_brackets.split(',', 1)
        self._split_lines = (self._opts.compound_boundaries != 'keep'
                             or self._opts.strip
                             or self._opts.empty_field_values
                             or self._opts.missing_field_values
                             or self._opts.input_fields
                             or self._opts.output_fields)
        self._encode_posattrs = (self._opts.encode_special_chars
                                 in ['all', 'pos'])
        self._encode_structattrs = (self._opts.encode_special_chars
                                    in ['all', 'struct'])
        self._special_char_encode_map = [
            (c, (opts.encoded_special_char_prefix
                 + unichr(i + opts.encoded_special_char_offset)))
            for (i, c) in enumerate(opts.special_chars)]
        if self._split_lines:
            self._make_pos_attr_converter()
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

    def _make_pos_attr_converter(self):

        def make_field_list(last):
            return ' '.join(str(fieldnum + 1) for fieldnum in range(last))

        copy_extra_fields = None
        output_fields = self._opts.output_fields
        if not self._opts.output_fields:
            copy_extra_fields = True
            if self._opts.compound_boundaries == 'remove':
                output_fields = [(make_field_list(self._opts.lemma_field)
                                  + ':noboundaries')]
            elif self._opts.compound_boundaries == 'new':
                output_fields = [(
                        make_field_list(self._opts.noncompound_lemma_field - 1)
                        + ' ' + str(self._opts.lemma_field) + ':noboundaries')]
        # print repr(output_fields)
        self._pos_attr_converter = PosAttrConverter(
            self._opts.input_fields, output_fields, strip=self._opts.strip,
            empty_values=self._opts.empty_field_values,
            missing_values=self._opts.missing_field_values,
            copy_extra_fields=copy_extra_fields)

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
            attrs = self._pos_attr_converter.convert(attrs)
            line = '\t'.join(attrs) + '\n'
        if self._opts.space:
            line = line.replace(' ', self._opts.space)
        if self._opts.angle_brackets:
            line = (line.replace('<', self._opts.angle_brackets[0])
                    .replace('>', self._opts.angle_brackets[1]))
        if self._encode_posattrs:
            line = self._encode_special_chars(line)
        if self._opts.replace_xml_character_entities:
            line = self._replace_character_entities(line)
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

    def _replace_character_entities(self, line):

        def replace_char_entity_ref(matchobj):
            name = matchobj.group(1)
            if name in self._xml_char_entities:
                return self._xml_char_entities[name]
            elif name[0] == '#':
                if name[1] == 'x':
                    return unichr(int(name[2:], base=16))
                else:
                    return unichr(int(name[1:]))
            else:
                return name

        line = re.sub(r'&(' + self._xml_char_entity_name_regex + r');',
                      replace_char_entity_ref, line)
        if self._opts.replace_xml_character_entities == 'all':
            line = re.sub(r'&(' + self._xml_char_entity_name_regex + r')(?=\s)',
                          replace_char_entity_ref, line)
        return line

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
    optparser.add_option('--input-fields', '--input-pos-attributes',
                         action='append', default=[])
    optparser.add_option('--output-fields', '--output-pos-attributes',
                         action='append', default=[])
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
    optparser.add_option('--replace-xml-character-entities', type='choice',
                         choices=['correct', 'all'])
    (opts, args) = optparser.parse_args()
    if opts.noncompound_lemma_field is None:
        if opts.compound_boundaries == 'remove':
            opts.noncompound_lemma_field = opts.lemma_field
        else:
            opts.noncompound_lemma_field = opts.lemma_field + 1
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
