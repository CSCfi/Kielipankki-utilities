# -*- coding: utf-8 -*-


"""
Classes for reading VRT input as XML (into an ElementTree).

The classes require that the structural attributes in the VRT are
strictly hierarchical, that is, no crossing elements. The input may
not contain XML declarations.
"""


import re
import io

import lxml.etree as etree

from korpimport.util import elem_at


class VrtXmlReader(object):

    """
    An abstract base class for reading VRT as XML.

    The class implements the context manager protocol for closing the
    input file if necessary at the end, and the iterator protocol
    iterating over the top-level elements in the input as XML.
    """

    _XML_DECL = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

    def __init__(self, filename_or_file, pos_attr_names=None,
                 number_tokens=False):
        self._file_opened = False
        if isinstance(filename_or_file, basestring):
            self._file = io.open(filename_or_file, 'rt', encoding='utf-8')
            self._file_opened = True
        else:
            self._file = filename_or_file
        self._pos_attr_names = pos_attr_names
        self._buf = bytearray()
        self._input_eof = False
        self._tokennum = 0 if number_tokens else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._file_opened:
            self.close()
        return False

    def __iter__(self):
        return self

    def next(self):
        # print 'next', self._input_eof
        if self._input_eof:
            raise StopIteration()
        else:
            # At EOF, VrtXmlSplitReader.read() returns an empty string
            # to etree.parse, which tries to parse it and raises an
            # XMLSyntaxError exception. At the end of the previous
            # split document, self._input_eof is not yet known.
            # Another option could be to use a lookahead line in
            # VrtXmlSplitReader.read and set self._input_eof if the
            # lookahead line is empty.
            try:
                return etree.parse(self)
            except etree.XMLSyntaxError as exc:
                if exc.msg.startswith('Document is empty'):
                    raise StopIteration()
                else:
                    raise

    def read(self, size):
        pass

    def close(self):
        self._file.close()

    def _xmlify_posattrs_line(self, line):
        if self._tokennum is not None:
            self._tokennum += 1
            numattr = ' num="' + str(self._tokennum) + '"'
        else:
            numattr = ''
        attrvals = line[:-1].split('\t')
        if self._pos_attr_names:
            attrstr = ''.join(
                (u'<attr name="'
                 + elem_at(self._pos_attr_names, attrnum, '') + '">'
                 + attrval + '</attr>')
                for attrnum, attrval in enumerate(attrvals))
        else:
            attrstr = ''.join((u'<attr>' + attrval + '</attr>')
                              for attrval in attrvals)
        return ('<token' + numattr + '>' + attrstr + '</token>\n')


class VrtXmlWrappedReader(VrtXmlReader):

    """Wrap the input VRT into a single top element for XML."""

    class _State(object):

        HEADER = 0
        BODY = 1
        FOOTER = 2
        EOF = 3

        def __init__(self):
            self._state = self.HEADER

        def __eq__(self, other):
            return self._state == other

    def __init__(self, filename_or_file, wrap_elem='__XML_ROOT__', **kwargs):
        super(VrtXmlWrappedReader, self).__init__(filename_or_file, **kwargs)
        self._wrap_elem = wrap_elem
        self._wrap_elem_open = b'<' + bytes(wrap_elem) + '>\n'
        self._wrap_elem_close = b'</' + bytes(wrap_elem) + '>\n'
        self._state = self._State()

    def read(self, size):
        if self._state == self._State.HEADER:
            self._append_header()
            self._state = self._State.BODY
        elif self._state == self._State.FOOTER:
            self._append_footer()
            self._state = self._State.EOF
        elif self._state == self._State.EOF:
            return b''
        else:
            while len(self._buf) < size and not self._input_eof:
                line = self._file.readline()
                if not line:
                    self._input_eof = True
                    self._state = self._State.FOOTER
                else:
                    if line[0] != '<':
                        line = self._xmlify_posattrs_line(line)
                    else:
                        self._tokennum = 0
                    self._buf.extend(line.encode('utf-8'))
        retval = bytes(self._buf[:size])
        del self._buf[:size]
        return retval

    def _append_header(self):
        self._buf = bytearray(self._XML_DECL + self._wrap_elem_open)

    def _append_footer(self):
        self._buf.extend(self._wrap_elem_close)


class VrtXmlSplitReader(VrtXmlReader):

    """Process each top-level s-attribute of the input VRT separately."""

    def __init__(self, filename_or_file, token_numbering_reset_regex=None,
                 **kwargs):
        super(VrtXmlSplitReader, self).__init__(filename_or_file, **kwargs)
        self._token_num_reset_re = token_numbering_reset_regex
        self._top_elem = None
        self._output_eof = False

    def read(self, size):
        # print 'read', size, self._input_eof, self._output_eof
        if self._output_eof:
            return b''
        while (len(self._buf) < size and not self._input_eof
               and not self._output_eof):
            line = self._file.readline()
            # print 'read2', repr(line)
            if not line:
                self._input_eof = True
            else:
                if line[0] == '<':
                    if line[1] == '/' and self._top_elem:
                        elem = line.strip('</>\n ')
                        if elem == self._top_elem:
                            self._output_eof = True
                            self._top_elem = None
                    elif self._top_elem is None:
                        mo = re.match(r'<(\w+)', line)
                        if mo:
                            self._top_elem = mo.group(1)
                        self._buf = bytearray(self._XML_DECL)
                    if re.match(self._token_num_reset_re, line):
                        self._tokennum = 0
                else:
                    line = self._xmlify_posattrs_line(line)
                self._buf.extend(line.encode('utf-8'))
        retval = bytes(self._buf[:size])
        del self._buf[:size]
        # print 'return', repr(retval), self._input_eof, self._output_eof
        return retval

    def next(self):
        self._output_eof = False
        return super(VrtXmlSplitReader, self).next()
