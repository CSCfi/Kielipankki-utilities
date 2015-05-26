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


class CharConverter(object):

    def __init__(self, opts, input_encoding='utf-8'):
        self._opts = opts
        self._input_encoding = input_encoding
        self._convert_posattrs = (self._opts.attribute_types
                                 in ['all', 'pos'])
        self._convert_structattrs = (self._opts.attribute_types
                                    in ['all', 'struct'])
        self._convert_map = [(c, (opts.prefix + unichr(i + opts.offset)))
                             for (i, c) in enumerate(opts.chars)]
        if opts.mode == 'decode':
            self._convert_map = [(enc, dec) for dec, enc in self._convert_map]

    def process_input(self, fnames):
        if not fnames:
            self._process_input(sys.stdin)
        else:
            for fname in fnames:
                with codecs.open(fname, 'r',
                                 encoding=self._input_encoding) as file_:
                    self._process_input(file_)

    def _process_input(self, file_):
        for line in file_:
            if line[0] == '<' and line.endswith('>\n'):
                if self._convert_structattrs:
                    line = self._convert_chars_in_struct_attrs(line)
            elif self._convert_posattrs:
                line = self._convert_chars(line)
            sys.stdout.write(line)

    def _convert_chars(self, s):
        """Encode the special characters in s."""
        return replace_substrings(s, self._convert_map)

    def _convert_chars_in_struct_attrs(self, s):
        """Encode the special characters in the double-quoted substrings
        of s.
        """
        return re.sub(r'("(?:[^\\"]|\\[\\"])*")',
                      lambda mo: self._convert_chars(mo.group(0)), s)


def getopts():
    usage = """%prog [options] input.vrt ... > output.vrt

Encode or decode in VRT files special characters that are problematic in CWB."""
    optparser = OptionParser(usage=usage)
    # TODO: Add an option to specify feature set attributes in which
    # vertical bars should not be encoded.
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


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    converter = CharConverter(opts, input_encoding)
    converter.process_input(args)


if __name__ == "__main__":
    main()
