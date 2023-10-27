#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# NOTE: This script is OBSOLETE; use ../vrt-tools/vrt-convert-chars
# instead.


# This script has been converted from Python 2 to Python 3.


# TODO:
# - Add an option not to decode encoded vertical bars in feature set
#   attributes to allow correct round-trip conversion.
# - Rewrite the script as a proper VRT tool.


import sys
import re
import errno

from optparse import OptionParser

import korpimport3.util as korputil


def replace_substrings(s, mapping):
    """Replace substrings in s according to mapping (a sequence of
    pairs (string, replacement): replace each string with the
    corresponding replacement.
    """
    for (s1, repl) in mapping:
        s = s.replace(s1, repl)
    return s


class CharConverter:

    _xml_char_entities = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '\'': '&apos;',
        '"': '&quot;'
        }

    def __init__(self, opts, input_encoding='utf-8-sig'):
        self._opts = opts
        self._input_encoding = input_encoding
        self._convert_posattrs = (self._opts.attribute_types
                                 in ['all', 'pos'])
        self._convert_structattrs = (self._opts.attribute_types
                                    in ['all', 'struct'])
        self._convert_map = [(c, (opts.prefix + chr(i + opts.offset)))
                             for (i, c) in enumerate(opts.chars)]
        self._add_xml_char_refs_to_convert_map()
        self._feat_set_attrs = set(
            self._make_attr_list(self._opts.feature_set_attributes))
        self._feat_set_struct_attrs = self._make_feat_set_struct_attrs()
        # print repr(self._feat_set_struct_attrs)
        if opts.mode == 'decode':
            self._convert_map = [(enc, dec) for dec, enc in self._convert_map]
        if (opts.mode == 'encode' and self._convert_posattrs
            and self._feat_set_attrs):
            self._convert_chars_in_pos_attrs = (
                self._convert_chars_in_pos_attrs_featsets)
        else:
            self._convert_chars_in_pos_attrs = self._convert_chars
        if (opts.mode == 'encode' and self._convert_structattrs
            and self._feat_set_struct_attrs):
            self._convert_chars_in_struct_attrs = (
                self._convert_chars_in_struct_attrs_featsets)
        else:
            self._convert_chars_in_struct_attrs = (
                self._convert_chars_in_struct_attrs_simple)
        self._convert_map_featset = [
            (dec, enc) for dec, enc in self._convert_map if dec != '|']
        self._struct_re = (
            (r'</?(?:' + '|'.join(re.split(r'\s*[\s,]\s*',
                                        self._opts.recognize_structs))
             + r')(?:\s.*)?/?>\s*$')
            if self._opts.recognize_structs else r'<.+>\s*$')

    def _make_attr_list(self, attrnumlist):
        if attrnumlist:
            return [int(numstr) - 1
                    for numstr in re.split(r'\s*[\s,]\s*', attrnumlist)]
        else:
            return []

    def _make_feat_set_struct_attrs(self):
        set_struct_attrs = {}
        for attr_spec_list in (self._opts.feature_set_struct_attributes or []):
            for attr_spec in attr_spec_list.split():
                if ':' in attr_spec:
                    elemname, attrnames_str = attr_spec.split(':', 1)
                    attrnames = re.split(r'[,+]', attrnames_str)
                    # A structural attribute specification for
                    # cwb-encode, recognized from the first element
                    # being numeric: only take the attribute names
                    # ending in a slash
                    if attrnames[0].isdigit():
                        attrnames = [attrname[:-1] for attrname in attrnames[1:]
                                     if attrname[-1] == '/']
                    else:
                        # Otherwise, allow but do not require a
                        # trailing slash
                        attrnames = [
                            attrname.strip('/') for attrname in attrnames]
                elif '_' in attr_spec:
                    elemname, attrname = attr_spec.split('_', 1)
                    attrnames = [attrname]
                if attrnames:
                    elem_attrs = set_struct_attrs.setdefault(elemname, set())
                    elem_attrs |= set(attrnames)
        return set_struct_attrs

    def _add_xml_char_refs_to_convert_map(self):
        if self._opts.convert_xml_char_refs:
            if self._opts.mode == 'encode':
                # When encoding, replace both literal characters and
                # XML character entity references with the encoded
                # characters.
                self._convert_map.extend(
                    (self._xml_char_entities[c1], c2)
                    for c1, c2 in self._convert_map
                    if c1 in self._xml_char_entities)
            else:
                # When decoding, replace the appropriate converted
                # characters with XML character entity references and
                # not the literal characters. The conversion map will
                # be inverted only after this.
                self._convert_map = [
                    (self._xml_char_entities.get(c1, c1), c2)
                    for c1, c2 in self._convert_map]

    def process_input(self, fnames):
        if not fnames:
            self._process_input(sys.stdin)
        else:
            for fname in fnames:
                with open(fname, 'r', encoding=self._input_encoding) as file_:
                    self._process_input(file_)

    def _process_input(self, file_):
        for line in korputil.whole_line_reader(file_):
            if line[0] == '<' and line.rstrip()[-1] == '>':
                # Note: This does not skip multi-line XML comments, as
                # cwb-encode does not recognize them
                if self._convert_structattrs and line[1] not in '!?':
                    line = self._convert_chars_in_struct_attrs(line)
            elif self._convert_posattrs:
                line = self._convert_chars_in_pos_attrs(line)
            sys.stdout.write(line)

    def _convert_chars(self, s, convert_map=None):
        """Encode the special characters in s."""
        return replace_substrings(s, convert_map or self._convert_map)

    def _convert_chars_in_pos_attrs_featsets(self, s):
        attrs = s.split('\t')
        for attrnum, attr in enumerate(attrs):
            attrs[attrnum] = replace_substrings(
                attr, (self._convert_map_featset
                       if attrnum in self._feat_set_attrs
                       else self._convert_map))
        return '\t'.join(attrs)

    def _convert_chars_in_struct_attrs_simple(self, s):
        """Encode the special characters in the double- or single-quoted
        substrings of s.
        """
        return re.sub(r'''(([\"\']).*?\2)''',
                      lambda mo: self._convert_chars(mo.group(0)), s)

    def _convert_chars_in_struct_attrs_featsets(self, s):

        def convert_attr(mo, convert_map=None, elemname=None):
            convert_map = convert_map or (
                self._convert_map_featset
                if (mo.group(1) in self._feat_set_struct_attrs.get(elemname,
                                                                   set()))
                else self._convert_map)
            # Strip possible whitespace around the equals sign.
            return (mo.group(1) + '='
                    + self._convert_chars(mo.group(2), convert_map))

        elemname = re.search(r'(\w+)', s).group(1)
        convert_map = (None if elemname in self._feat_set_struct_attrs
                       else self._convert_map)
        # print elemname, convert_map
        return re.sub(r'''(\w+)\s*=\s*(".*?"|'.*?')''',
                      lambda mo: convert_attr(mo, convert_map, elemname), s)


def getopts():
    usage = """%prog [options] input.vrt ... > output.vrt

This script is OBSOLETE; please use ../vrt-tools/vrt-convert-chars instead.

Encode or decode in VRT files special characters that are problematic in CWB."""
    optparser = OptionParser(usage=usage)
    optparser.add_option(
        '--attribute-types', type='choice', choices=['all', 'pos', 'struct'],
        default='all', metavar='TYPE',
        help=('convert special characters in TYPE attributes, where TYPE is'
              ' one of: pos (positional attributes only), struct (structural'
              ' attributes only), or all (both positional and structural'
              ' attributes) (default: %default)'))
    optparser.add_option(
        '--chars', default=' /<>|',
        help=('the characters to be converted in their unencoded form'
              ' (default: "%default")'))
    optparser.add_option(
        '--offset', default='0x7F',
        help=('the code point offset for the encoded characters: the first'
              ' character in CHARS is encoded as OFFSET, the second as'
              ' OFFSET+1 and so on (default: %default)'))
    optparser.add_option(
        '--prefix', default='',
        help='prefix the encoded characters with PREFIX (default: none)')
    optparser.add_option(
        '--no-convert-xml-character-entity-references', '--no-xml-char-refs',
        dest='convert_xml_char_refs', default=True, action='store_false',
        help=('do not encode XML character entity references that correspond '
              ' to special characters to be encoded'))
    optparser.add_option(
        '--feature-set-attributes', '--feature-set-attrs',
        metavar='ATTRNUMLIST',
        help=('do not encode vertical bars in positional attributes whose'
              ' numbers are listed in ATTRNUMLIST, separated by spaces or'
              ' commas; attribute numbering begins from 1'))
    optparser.add_option(
        '--feature-set-struct-attributes', '--set-struct-atrrs',
        action='append', default=[],
        help=('Treat the structural attributes specified in the attribute'
              ' specification ATTRSPEC as feature-set attributes and do not'
              ' convert the vertical bar characters in them.'
              ' ATTRSPEC is a space-separated list of element definitions, of'
              ' the form ELEMNAME_ATTRNAME, ELEMNAME:ATTRNAMELIST or'
              ' ELEMNAME:N+ATTRNAMELIST, where'
              ' ELEMNAME is the name of the XML element, ATTRNAME is a single'
              ' attribute name and ATTRNAMELIST is a list of attribute names'
              ' separated by commas or pluses. The third form corresponds to'
              ' a structural attribute specification for cwb-encode where N'
              ' is a non-negative integer (ignored), and the feature-set'
              ' attribute names in ATTRNAMELIST must be suffixed by a slash;'
              ' others are ignored. In contrast, in the second form, all the'
              ' attributes listed in ATTRLIST are considered feature-set'
              ' attributes regardless of whether they end in a slash or not.'
              ' For example, the values "elem_attr1 elem_attr2",'
              ' "elem:attr1,attr2" and "elem:0+attr0+attr1/+attr2/" are'
              ' equivalent.'
              ' This option can be repeated.'),
        metavar='ATTRSPEC')
    optparser.add_option(
        '--recognize-structs',
        metavar='STRUCTLIST',
        help=('recognize only the structural attribute names listed in'
              ' STRUCTLIST, separated by spaces or commas; the characters in'
              ' all other XML-tag-like tokens are encoded as positional'
              ' attributes; by default, treat all lines beginning with < and'
              ' ending in > as structural tags'))
    optparser.add_option(
        '--mode', type='choice', choices=['encode', 'decode'], default='encode',
        help=('MODE specifies the direction of conversion: encode or decode'
              ' (default: %default)'))
    optparser.add_option(
        '--encode', action='store_const', dest='mode', const='encode',
        help='shorthand for --mode=encode')
    optparser.add_option(
        '--decode', action='store_const', dest='mode', const='decode',
        help='shorthand for --mode=decode')
    (opts, args) = optparser.parse_args()
    opts.offset = int(opts.offset, base=0)
    return opts, args


def main_main():
    input_encoding = 'utf-8-sig'
    output_encoding = 'utf-8'
    korputil.set_sys_stream_encodings(
        input_encoding, output_encoding, output_encoding)
    (opts, args) = getopts()
    converter = CharConverter(opts, input_encoding)
    converter.process_input(args)


def main():
    try:
        main_main()
    except IOError as e:
        if e.errno == errno.EPIPE:
            sys.stderr.write('Broken pipe\n')
        else:
            sys.stderr.write(str(e) + '\n')
        exit(1)
    except KeyboardInterrupt as e:
        sys.stderr.write('Interrupted\n')
        exit(1)
    except:
        raise


if __name__ == "__main__":
    main()
