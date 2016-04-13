#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re
import errno

from optparse import OptionParser
from collections import defaultdict

from korpimport.util import unique


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


def fix_feature_set_attr(value, unique_opt=None):
    if not value:
        value = '|'
    else:
        if value[0] != '|':
            value = '|' + value
        if value[-1] != '|':
            value += '|'
        if unique_opt is not None:
            values = unique(value[1:-1].split('|'))
            # full: always remove duplicates; partial: remove
            # duplicates only if all values are the same
            if unique_opt == 'full' or (unique_opt == 'partial'
                                        and len(values) == 1):
                value = '|' + '|'.join(values) + '|'
    return value


class PosAttrConverter(object):

    class OutputFieldSpec(object):

        def __init__(self, fieldspec, input_field_nums=None,
                     char_encode_maps=None, compound_boundary_marker=None,
                     compound_boundary_hyphen=False):
            self._input_field_nums = input_field_nums or {}
            self._char_encode_maps = char_encode_maps or {'set': [], 'base': []}
            self._compound_boundary_re = re.compile(compound_boundary_marker or
                                                    re.escape('#'))
            self._make_lemma_without_boundaries = (
                self._make_lemma_without_boundaries_tdt
                if compound_boundary_hyphen
                else self._make_lemma_without_boundaries_simple)
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
                if key == 'unique' and not val:
                    val = 'partial'
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
                    # sys.stderr.write(result)
                    result = self._make_lemma_without_boundaries(
                        result,
                        input_fields[self._input_field_nums.get('word')])
                    # sys.stderr.write(' -> ' + result + '\n')
                if 'set' in self._opts or 'setconvert' in self._opts:
                    result = fix_feature_set_attr(result,
                                                  self._opts.get('unique'))
                elif 'setfirst' in self._opts:
                    if result.startswith('|'):
                        result = result[1:]
                    result = result.split('|', 1)[0]
                elif 'setlast' in self._opts:
                    if result.endswith('|'):
                        result = result[:-1]
                    result = result.split('|')[-1]
                if self._opts.get('setconvert'):
                    result = result.replace('|', self._opts['setconvert'])
                if 'set' in self._opts:
                    if self._char_encode_maps['set']:
                        result = replace_substrings(
                            result, self._char_encode_maps['set'])
                elif self._char_encode_maps['base']:
                    result = replace_substrings(
                        result, self._char_encode_maps['base'])
            return result

        def _make_lemma_without_boundaries_simple(self, lemma, wordform):
            return (self._compound_boundary_re.sub('', lemma)
                    if len(lemma) > 2
                    else lemma)

        # Adapted from vrt-add-parses.py
        def _make_lemma_without_boundaries_tdt(self, lemma, wordform):
            if len(lemma) < 3 or not self._compound_boundary_re.search(lemma):
                return lemma
            elif '-' not in wordform:
                return self._compound_boundary_re.sub('', lemma)
            else:
                # In some cases, the lemma has - replaced with a |; in
                # other cases not
                wordform_parts = wordform.split('-')
                lemma_parts = self._compound_boundary_re.split(lemma)
                if (len(wordform_parts) == len(lemma_parts)
                    and '-' not in lemma):
                    return self._compound_boundary_re.sub('-', lemma)
                else:
                    lemma_without_boundaries = [lemma_parts[0]]
                    lemma_prefix_len = len(lemma_parts[0])
                    wf_prefix_len = len(wordform_parts[0])
                    wf_partnr = 1
                    for lemma_part in lemma_parts[1:]:
                        if wf_partnr >= len(wordform_parts):
                            lemma_without_boundaries.append(lemma_part)
                        elif (lemma_part[:2] == wordform_parts[wf_partnr][:2]
                              and abs(wf_prefix_len - lemma_prefix_len) <= 2):
                            # FIXME: Devise a better heuristic
                            lemma_without_boundaries.extend(['-', lemma_part])
                            wf_prefix_len += len(wordform_parts[wf_partnr])
                            wf_partnr += 1
                        else:
                            lemma_without_boundaries.append(lemma_part)
                        lemma_prefix_len += len(lemma_part)
                    return ''.join(lemma_without_boundaries)

        def get_input_fieldnum(self):
            return self._input_fieldnum

        def __repr__(self):
            return str(self._input_fieldnum) + ':' + repr(self._opts)

    def __init__(self, input_fields, output_fields, strip=False,
                 empty_values=None, missing_values=None,
                 copy_extra_fields=None, char_encode_maps=None,
                 compound_boundary_marker=None,
                 compound_boundary_hyphen=False):
        self._compound_boundary_marker = compound_boundary_marker
        self._compound_boundary_hyphen = compound_boundary_hyphen
        self._make_input_fields(input_fields)
        self._copy_extra_fields = value_or_default(copy_extra_fields,
                                                   not output_fields)
        self._empty_field_values = self._make_default_field_values(empty_values)
        self._missing_field_values = self._make_default_field_values(
            missing_values)
        self._make_output_fields(output_fields, char_encode_maps)
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
                self.OutputFieldSpec(
                    str(num + 1), self._input_fields,
                    compound_boundary_marker=self._compound_boundary_marker,
                    compound_boundary_hyphen=self._compound_boundary_hyphen))
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

    def _make_output_fields(self, output_fieldslist, char_encode_maps):
        self._output_fields = []
        output_field_kwargs = dict(
            char_encode_maps=char_encode_maps,
            compound_boundary_marker=self._compound_boundary_marker,
            compound_boundary_hyphen=self._compound_boundary_hyphen)
        if output_fieldslist:
            for fields in output_fieldslist:
                fieldspecs = re.findall(r'(?:\S|\'[^\']+\'|"[^\"]+")+', fields)
                # print repr(fieldspecs)
                for fieldspec in fieldspecs:
                    self._output_fields.append(
                        self.OutputFieldSpec(
                            fieldspec, self._input_fields,
                            **output_field_kwargs))
        self._extra_output_field = self.OutputFieldSpec(
            '0', self._input_fields, **output_field_kwargs)

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
        self._special_char_encode_maps = {}
        self._special_char_encode_maps['base'] = [
            (c, (opts.encoded_special_char_prefix
                 + unichr(i + opts.encoded_special_char_offset)))
            for (i, c) in enumerate(opts.special_chars)]
        self._special_char_encode_maps['set'] = [
            (key, val) for key, val in self._special_char_encode_maps['base']
            if key != '|']
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
        self._set_struct_attrs = self._init_set_struct_attrs()
        self._init_struct_attr_copy_info()

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
        char_encode_maps = (
            self._special_char_encode_maps if self._encode_posattrs
            else None)
        self._pos_attr_converter = PosAttrConverter(
            self._opts.input_fields, output_fields, strip=self._opts.strip,
            empty_values=self._opts.empty_field_values,
            missing_values=self._opts.missing_field_values,
            copy_extra_fields=copy_extra_fields,
            char_encode_maps=char_encode_maps,
            compound_boundary_marker=self._opts.compound_boundary_marker,
            compound_boundary_hyphen=self._opts.compound_boundary_hyphen)

    def _init_set_struct_attrs(self):
        set_struct_attrs = {}
        if self._opts.set_struct_attributes:
            for attr_spec_list in self._opts.set_struct_attributes:
                for attr_spec in attr_spec_list.split():
                    if ':' in attr_spec:
                        elemname, attrnames_str = attr_spec.split(':', 1)
                        attrnames = set(re.split(r'[,+]', attrnames_str))
                        elem_attrs = set_struct_attrs.setdefault(elemname,
                                                                 set())
                        elem_attrs |= attrnames
                    elif '_' in attr_spec:
                        elemname, attrname = attr_spec.split('_', 1)
                        elem_attrs = set_struct_attrs.setdefault(elemname,
                                                                 set())
                        elem_attrs |= set([attrname])
        return set_struct_attrs

    def _init_struct_attr_copy_info(self):
        self._struct_attr_values = defaultdict(dict)
        self._struct_attr_copy_sources = defaultdict(set)
        self._struct_attr_copy_targets = defaultdict(list)
        for copyspec in self._opts.copy_struct_attribute:
            target, sources = re.split(r'\s*:\s*', copyspec, 1)
            sourcelist = re.split(r'\s*;\s*', sources)
            for source in sourcelist:
                elem, attrs = re.split(r'\s*/\s*', source, 1)
                attrlist = re.split(r'\s*,\s*', attrs)
                for attr in attrlist:
                    self._struct_attr_copy_sources[elem].add(attr)
                    self._struct_attr_copy_targets[target].append((elem, attr))
        # print self._struct_attr_copy_sources, self._struct_attr_copy_targets

    def process_files(self, files):
        if isinstance(files, list):
            for file_ in files:
                self.process_files(file_)
        elif isinstance(files, basestring):
            with codecs.open(files, 'r', encoding='utf-8',
                             errors=self._opts.encoding_errors) as f:
                self._fix_input(f)
        else:
            self._fix_input(files)

    def _fix_input(self, f):
        linenr = 1
        try:
            for line in f:
                sys.stdout.write(self._make_fixed_line(line))
                linenr += 1
        except SyntaxError:
            raise
        except Exception:
            sys.stderr.write(
                ('{prog}: An exception occurred while processing file {fname}'
                 ', line {linenr} (approximately):\n')
                .format(prog=sys.argv[0], fname=f.name, linenr=linenr))
            raise

    def _make_fixed_line(self, line):
        if line.startswith('<') and line.rstrip().endswith('>'):
            line = self._fix_structattrs(line.rstrip()) + '\n'
            if self._encode_structattrs and line[1] != '/':
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
        if self._opts.replace_xml_character_entities:
            line = self._replace_character_entities(line)
        if self._encode_posattrs and not self._split_lines:
            line = self._encode_special_chars(line)
        return line

    def _encode_special_chars(self, s, encode_map_key='base'):
        """Encode the special characters in s."""
        return replace_substrings(
            s, self._special_char_encode_maps.get(encode_map_key, []))

    def _encode_special_chars_in_struct_attrs(self, s):
        """Encode the special characters in the double-quoted substrings
        of s.
        """

        def encode_attr(mo, encode_map_key=None, elemname=None):
            return self._encode_special_chars(
                mo.group(0),
                encode_map_key or (
                    'set' if (mo.group(2) in
                              self._set_struct_attrs.get(elemname, set()))
                    else 'base'))

        elemname = re.search(r'(\w+)', s).group(1)
        if elemname in self._set_struct_attrs:
            return re.sub(
                r'((\w+)="(?:[^\\"]|\\[\\"])*")',
                lambda mo: encode_attr(mo, elemname=elemname),
                s)
        else:
            return re.sub(
                r'("(?:[^\\"]|\\[\\"])*")',
                lambda mo: encode_attr(mo, encode_map_key='base'),
                s)

    def _replace_character_entities(self, line):

        def replace_char_entity_ref(matchobj):
            name = matchobj.group(1)
            if name in self._xml_char_entities:
                return self._xml_char_entities[name]
            elif name[0] == '#':
                chrval = (int(name[2:], base=16)
                          if name[1] == 'x'
                          else int(name[1:]))
                try:
                    return unichr(chrval)
                except ValueError:
                    return name
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
        if line.startswith('</'):
            if self._struct_attr_values:
                elemname = line[2:-2]
                if elemname in self._struct_attr_values:
                    del self._struct_attr_values[elemname]
        else:
            if self._elem_ids:
                line = self._add_elem_id(line)
            if self._struct_attr_copy_sources:
                line = self._copy_struct_attrs(line)
            if self._set_struct_attrs:
                line = self._fix_set_struct_attrs(line)
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
            line = self._add_attrs(line,
                                   [('id', str(self._elem_ids[elemname]))])
        return line

    def _add_attrs(self, line, attrs):
        return (line[:-1] + ' '
                + ' '.join(name + '="' + val + '"' for name, val in attrs)
                + line[-1:])

    def _copy_struct_attrs(self, line):
        # print self._struct_attr_values
        elemname = re.search(r'(\w+)', line).group(1)
        if elemname in self._struct_attr_copy_sources:
            self._struct_attr_values[elemname] = \
                self._extract_struct_attrs(line)
        if elemname in self._struct_attr_copy_targets:
            line = self._add_attrs(
                line, [(src_elem + '_' + attrname, value)
                       for (src_elem, attrname, value)
                       in self._get_struct_attr_values(
                        self._struct_attr_copy_targets[elemname])])
        return line

    def _extract_struct_attrs(self, line):
        return dict(re.findall(r'(\w+)=\"([^\"]+)\"', line))

    def _get_struct_attr_values(self, elem_attrname_list):
        result = []
        for elem, attrname in elem_attrname_list:
            if elem in self._struct_attr_values:
                if attrname == '*':
                    result.extend(
                        [(elem, name, val) for name, val
                         in sorted(self._struct_attr_values[elem].items())])
                else:
                    result.append(
                        (elem, attrname,
                         self._struct_attr_values[elem].get(attrname, '')))
        return result

    def _fix_set_struct_attrs(self, line):

        def fix_vbars(mo, feat_set_attrs):
            if mo.group(1) in feat_set_attrs:
                return (mo.group(1) + '="' + fix_feature_set_attr(mo.group(2))
                        + '"')
            else:
                return mo.group(0)

        elemname = re.search(r'(\w+)', line).group(1)
        if elemname in self._set_struct_attrs:
            return re.sub(
                r'(\w+)="((?:[^\\"]|\\[\\"])*)"',
                lambda mo: fix_vbars(mo, self._set_struct_attrs[elemname]),
                line)
        else:
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
    optparser.add_option('--compound-boundary-marker', '--compound-marker',
                         default='#')
    optparser.add_option('--compound-boundary-regexp', action='store_true')
    optparser.add_option('--compound-boundary-hyphen',
                         '--compound-boundary-can-replace-hyphen',
                         action='store_true')
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
    optparser.add_option(
        '--set-struct-attributes', '--feature-set-valued-struct-attributes',
        action='append', default=[],
        help=('Treat the structural attributes specified in the attribute'
              ' specification ATTRSPEC as feature set attributes and do not'
              ' convert the vertical bar characters in them.'
              ' ATTRSPEC is a space-separated list of element definitions, of'
              ' the form ELEMNAME_ATTRNAME or ELEMNAME:ATTRNAMELIST, where'
              ' ELEMNAME is the name of the XML element, ATTRNAME is a single'
              ' attribute name and ATTRNAMELIST is a list of attribute names'
              ' separated by commas or pluses.'
              ' The first form can be used to specify multiple feature set'
              ' attributes for a single element type: for example, the values'
              ' "elem_attr1 elem_attr2" and "elem:attr1,attr2" are equivalent.'
              ' This option can be repeated.'),
        metavar='ATTRSPEC')
    optparser.add_option('--empty-field-values')
    optparser.add_option('--missing-field-values')
    optparser.add_option('--rename-element', action='append', default=[])
    optparser.add_option('--add-element-id', '--add-elem-id', action='append',
                         default=[])
    optparser.add_option('--replace-xml-character-entities', type='choice',
                         choices=['correct', 'all'])
    optparser.add_option('--copy-struct-attribute', action='append', default=[])
    optparser.add_option('--encoding-errors', '--character-encoding-errors',
                         type='choice', choices=['strict', 'replace', 'ignore'],
                         default='strict')
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
    if not opts.compound_boundary_regexp:
        opts.compound_boundary_marker = re.escape(opts.compound_boundary_marker)
    return (opts, args)


def main_main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    attr_fixer = AttributeFixer(opts)
    attr_fixer.process_files(args if args else sys.stdin)


def main():
    try:
        main_main()
    except IOError, e:
        if e.errno == errno.EPIPE:
            sys.stderr.write('Broken pipe\n')
        else:
            sys.stderr.write(str(e) + '\n')
        exit(1)
    except KeyboardInterrupt, e:
        sys.stderr.write('Interrupted\n')
        exit(1)
    except:
        raise


if __name__ == "__main__":
    main()
