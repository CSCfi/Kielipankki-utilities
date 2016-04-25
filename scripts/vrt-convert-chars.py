#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re
import errno

from optparse import OptionParser

import korpimport.util as korputil


def replace_substrings(s, mapping):
    """Replace substrings in s according to mapping (a sequence of
    pairs (string, replacement): replace each string with the
    corresponding replacement.
    """
    for (s1, repl) in mapping:
        s = s.replace(s1, repl)
    return s


class CharConverter(object):

    _xml_char_entities = {
        '&': 'amp',
        '<': 'lt',
        '>': 'gt',
        '\'': 'apos',
        '"': 'quot'
        }

    def __init__(self, opts, input_encoding='utf-8'):
        self._opts = opts
        self._input_encoding = input_encoding
        self._convert_posattrs = (self._opts.attribute_types
                                 in ['all', 'pos'])
        self._convert_structattrs = (self._opts.attribute_types
                                    in ['all', 'struct'])
        self._convert_map = [(c, (opts.prefix + unichr(i + opts.offset)))
                             for (i, c) in enumerate(opts.chars)]
        self._add_xml_char_refs_to_convert_map()
        self._feat_set_attrs = set(
            self._make_attr_list(self._opts.feature_set_attributes))
        if opts.mode == 'decode':
            self._convert_map = [(enc, dec) for dec, enc in self._convert_map]
        if (opts.mode == 'encode' and self._convert_posattrs
            and self._feat_set_attrs):
            self._convert_chars_in_pos_attrs = (
                self._convert_chars_in_pos_attrs_featsets)
        else:
            self._convert_chars_in_pos_attrs = self._convert_chars
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

    def _add_xml_char_refs_to_convert_map(self):
        if self._opts.convert_xml_char_refs:
            xml_chars = []
            for c1, c2 in self._convert_map:
                if c1 in self._xml_char_entities:
                    xml_chars.append((c1, c2))
            self._convert_map.extend(
                ('&' + self._xml_char_entities[c1] + ';', c2)
                for c1, c2 in xml_chars)

    def process_input(self, fnames):
        if not fnames:
            self._process_input(sys.stdin)
        else:
            for fname in fnames:
                with codecs.open(fname, 'r',
                                 encoding=self._input_encoding) as file_:
                    self._process_input(file_)

    def _process_input(self, file_):
        for line in korputil.whole_line_reader(file_):
            if line[0] == '<' and line.rstrip()[-1] == '>':
                if self._convert_structattrs:
                    line = self._convert_chars_in_struct_attrs(line)
            elif self._convert_posattrs:
                line = self._convert_chars_in_pos_attrs(line)
            sys.stdout.write(line)

    def _convert_chars(self, s):
        """Encode the special characters in s."""
        return replace_substrings(s, self._convert_map)

    def _convert_chars_in_pos_attrs_featsets(self, s):
        attrs = s.split('\t')
        for attrnum, attr in enumerate(attrs):
            attrs[attrnum] = replace_substrings(
                attr, (self._convert_map_featset
                       if attrnum in self._feat_set_attrs
                       else self._convert_map))
        return '\t'.join(attrs)

    def _convert_chars_in_struct_attrs(self, s):
        """Encode the special characters in the double- or single-quoted
        substrings of s.
        """
        return re.sub(r'''(([\"\']).*?\2)''',
                      lambda mo: self._convert_chars(mo.group(0)), s)


def getopts():
    usage = """%prog [options] input.vrt ... > output.vrt

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
        '--chars', default=u' /<>|',
        help=('the characters to be converted in their unencoded form'
              ' (default: "%default")'))
    optparser.add_option(
        '--offset', default='0x7F',
        help=('the code point offset for the encoded characters: the first'
              ' character in CHARS is encoded as OFFSET, the second as'
              ' OFFSET+1 and so on (default: %default)'))
    optparser.add_option(
        '--prefix', default=u'',
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
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    converter = CharConverter(opts, input_encoding)
    converter.process_input(args)


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
