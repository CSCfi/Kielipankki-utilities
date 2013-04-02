#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import re


def replace_substrings(s, mapping):
    """Replace substrings in s according to mapping (a sequence of
    pairs (string, replacement): replace each string with the
    corresponding replacement.
    """
    sys.stderr.write(repr(type(s)) + '|' + repr(s) + '\n')
    for (s1, repl) in mapping:
        sys.stderr.write(repr(type(s1)) + '|' + repr(type(repl)) + '\n')
        s = s.replace(s1, repl)
    return s


class WrappedXMLFileReader(object):

    """Wrap file input into an XML element.

    Used to provide a dummy root element for concatenated XML files.
    The XML declarations of the files are removed except for the first
    one.
    """

    ST_AT_START = 0
    ST_AT_PREFIX = 1
    ST_IN_FILE = 2
    ST_AT_SUFFIX = 3
    ST_EOF = 4

    def __init__(self, f, wrapper_elem=None, mapping=None,
                 replace_reserved=False):
        self._f = f
        self._prefix = '<' + wrapper_elem + '>\n' if wrapper_elem else ''
        self._suffix = '</' + wrapper_elem + '>\n' if wrapper_elem else ''
        self._mapping = mapping
        self._replace_reserved = replace_reserved
        self._read_ahead = None
        self._state = self.ST_AT_START if wrapper_elem else self.ST_IN_FILE

    def read(self, size=-1):
        return self._base_read(self._f.read, size)

    def readline(self, size=-1):
        return self._base_read(self._f.readline, size)

    def _base_read(self, read_fn, size=-1):
        # FIXME: This does not take into account the interaction
        # between size and the prefix and suffix.
        if self._state == self.ST_AT_START:
            # Get the XML declaration if any
            text = self._replace_reserved_chars(self._f.readline())
            if text.startswith('<?xml'):
                mo = re.match(r'(<\?xml.*?\?>\n?)(.*)', text, re.DOTALL)
                if mo is not None:
                    (xmldecl, rest) = (mo.group(1), mo.group(2))
                    self._state = self.ST_AT_PREFIX
                    self._read_ahead = rest
                    return xmldecl
            else:
                self._state = self.ST_IN_FILE
                self._read_ahead = text
                return self._prefix
        elif self._state == self.ST_AT_PREFIX:
            self._state = self.ST_IN_FILE
            return self._prefix
        elif self._state == self.ST_IN_FILE:
            if self._read_ahead:
                text = self._read_ahead
                self._read_ahead = None
            else:
                text = self._replace_reserved_chars(read_fn(size))
                if text == '':
                    text = self._suffix
                    self._state = self.ST_EOF
            # Remove all further XML declarations (from concatenated
            # files); assumes that they are the same as the first one.
            text = re.sub(r'(<\?xml.*?\?>\n?)', '', text)
            return self._map_substrings(text)
        elif self._state == self.ST_EOF:
            return ''

    def _replace_reserved_chars(self, text):
        if self._replace_reserved:
            text = re.sub(r'&([^\w#])', r'&amp;\1', text)
            text = re.sub(r'<([^\w/])', r'&lt;\1', text)
        return text

    def _map_substrings(self, s):
        return replace_substrings(s, self._mapping) if self._mapping else s

    # TODO: Implement next()

    def __iter__(self):
        return self

    def __getattr__(self, name):
        """Pass all other attribute references to self._f."""
        return getattr(self._f, name)


def main():
    # For testing
    f = WrappedXMLFileReader(sys.stdin, wrapper_elem='__DUMMY__')
    while True:
        line = f.read()
        sys.stdout.write(line)
        if not line:
            break


if __name__ == '__main__':
    main()
