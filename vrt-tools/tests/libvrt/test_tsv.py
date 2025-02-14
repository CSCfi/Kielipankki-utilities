
"""
test_tsv.py

Pytest tests for library module `libvrt.tsv`.
"""


import os

import pytest

from collections import OrderedDict
from tempfile import NamedTemporaryFile

from libvrt.metaline import escape

import libvrt.tsv as tsv


@pytest.fixture
def infile():
    """Fixture as factory yielding function to create temporary file.

    The factory function takes as its argument the content (`bytes`)
    of the temporary file and returns it name.

    Removes all the created files at teardown.
    """

    # Names of created files
    files = []

    def _infile(content):
        """Return the name of a temporary file with `content` as content."""
        with NamedTemporaryFile('wb', delete=False) as ntf:
            ntf.write(content)
        files.append(ntf.name)
        return ntf.name

    yield _infile
    # Cleanup: remove created files
    for file_ in files:
        os.remove(file_)


@pytest.fixture
def open_infile(infile):
    """Fixture as factory yielding function to create and open a file.

    The factory function takes as its argument the content (`bytes`)
    and additional arguments and keyword arguments to `open` (after
    mode which is always ``rb``).

    Closes all the opened files at teardown.
    """

    # Opened files
    files = []

    def _open_infile(content, *args, **kwargs):
        """Return opened file with `content`, `*args`, `**kwargs` to `open`."""
        file_ = open(infile(content), 'rb', *args, **kwargs)
        files.append(file_)
        file_.__enter__()
        return file_

    yield _open_infile
    # Cleanup: close opened files
    for file_ in files:
        file_.__exit__(None, None, None)


class TestTsvReader:

    """Tests for `vrtlib.tsv.TsvReader`."""

    def _test_tsv_content(self, reader, fieldnames, content, heading_row=False):
        """Test that TSV file with `content` is read correctly by `reader`.

        `reader` is a `TsvReader` for reading a TSV file with content
        `content` (`bytes` or sequence of `bytes`) and with fields
        named as `fieldnames` (`list` of `bytes`). If `heading_row` is
        `True`, the first row of the file (and `content`) is a heading
        row with field names.

        This is an auxiliary test method containing assertions, called
        by the actual test methods.
        """
        if not heading_row:
            assert reader.fieldnames == fieldnames
        if isinstance(content, bytes):
            content = content.rstrip(b'\n').split(b'\n')
        for linenum, fields in enumerate(content):
            if linenum == 0 and heading_row:
                continue
            if isinstance(fields, bytes):
                fields = fields.rstrip(b'\n').split(b'\t')
            fileline = next(reader)
            assert reader.line_num == linenum + 1
            assert isinstance(fileline, OrderedDict)
            for fieldnum, fieldname in enumerate(fieldnames):
                assert fileline[fieldname] == fields[fieldnum]
        if heading_row:
            assert reader.fieldnames == fieldnames
        with pytest.raises(StopIteration):
            d = next(reader)

    def test_fieldnames_arg(self, open_infile):
        """Test `TsvReader` with field names as an argument."""
        fieldnames = [b'a', b'b', b'c']
        content = (b'aa\tbb\tcc\n'
                   b'dd\tee\tff\n')
        with open_infile(content) as inf:
            reader = tsv.TsvReader(inf, fieldnames=fieldnames)
            # Also test TsvReader.read_fieldnames()
            assert reader.read_fieldnames() == fieldnames
            self._test_tsv_content(reader, fieldnames, content)

    def test_fieldnames_arg_empty(self, open_infile):
        """Test `TsvReader`, field names as argument, empty input file."""
        fieldnames = [b'a', b'b', b'c']
        content = b''
        with open_infile(content) as inf:
            reader = tsv.TsvReader(inf, fieldnames=fieldnames)
            assert reader.read_fieldnames() == fieldnames
            with pytest.raises(StopIteration):
                d = next(reader)

    def test_fieldnames_heading_row(self, open_infile):
        """Test `TsvReader` with field names in a heading row."""
        fieldnames = [b'a', b'b', b'c']
        content = (b'a\tb\tc\n'
                   b'aa\tbb\tcc\n'
                   b'dd\tee\tff\n')
        with open_infile(content) as inf:
            reader = tsv.TsvReader(inf)
            self._test_tsv_content(reader, fieldnames, content, True)

    def test_fieldnames_heading_row_empty(self, open_infile):
        """Test `TsvReader`, field names in a heading row, empty rest."""
        fieldnames = [b'a', b'b', b'c']
        content = b'a\tb\tc\n'
        with open_infile(content) as inf:
            reader = tsv.TsvReader(inf)
            with pytest.raises(StopIteration):
                d = next(reader)
            assert reader.fieldnames == fieldnames

    def test_read_fieldnames(self, open_infile):
        """Test `TsvReader.read_fieldnames`."""
        fieldnames = [b'a', b'b', b'c']
        content = (b'a\tb\tc\n'
                   b'aa\tbb\tcc\n'
                   b'dd\tee\tff\n')
        with open_infile(content) as inf:
            reader = tsv.TsvReader(inf)
            assert reader.read_fieldnames() == fieldnames
            self._test_tsv_content(reader, fieldnames, content, True)

    def test_encode_entities_always(self, open_infile):
        """Test `TsvReader` always encoding entities."""
        fieldnames = [b'a', b'b', b'c']
        content = [b'a\tb\tc\n',
                   b'"\tb<\t>c&\n',
                   b'a&lt;b\te&gt;e\tf&quot;f&amp;\n']
        content_joined = b''.join(content)
        content_enc = [escape(line) for line in content]
        # Always encoding entities
        for entities in [None, tsv.EncodeEntities.ALWAYS]:
            with open_infile(content_joined) as inf:
                reader = tsv.TsvReader(inf, entities=entities)
                assert reader.read_fieldnames() == fieldnames
                self._test_tsv_content(
                    reader, fieldnames, content_enc, True)

    def test_encode_entities_non_entities(self, open_infile):
        """Test `TsvReader` encoding entities but no & in existing ones."""
        fieldnames = [b'a', b'b', b'c']
        content = [b'a\tb\tc\n',
                   b'"\tb<\t>c&\n',
                   # &'s in the following are not encoded
                   b'a&lt;b\te&gt;e\tf&quot;f&amp;\n']
        content_joined = b''.join(content)
        content_enc = [content[0], escape(content[1]), content[2]]
        with open_infile(content_joined) as inf:
            reader = tsv.TsvReader(
                inf, entities=tsv.EncodeEntities.NON_ENTITIES)
            assert reader.read_fieldnames() == fieldnames
            self._test_tsv_content(reader, fieldnames, content_enc, True)

    def test_encode_entities_never(self, open_infile):
        """Test `TsvReader` never encoding entities."""
        fieldnames = [b'a', b'b', b'c']
        content = [b'a\tb\tc\n',
                   b'"\tb<\t>c&\n',
                   b'a&lt;b\te&gt;e\tf&quot;f&amp;\n']
        content_joined = b''.join(content)
        with open_infile(content_joined) as inf:
            reader = tsv.TsvReader(inf, entities=tsv.EncodeEntities.NEVER)
            assert reader.read_fieldnames() == fieldnames
            self._test_tsv_content(reader, fieldnames, content, True)

    def test_duplicate_fieldnames_arg(self, open_infile):
        """Test handling duplicate fieldnames given as `fieldnames`."""

        def asserts(reader, fieldnames):
            # Assertions common to two test cases
            assert reader.read_fieldnames() == fieldnames
            fields = next(reader)
            assert fields[b'a'] == b'cc'
            assert fields[b'b'] == b'bb'

        fieldnames = [b'a', b'b', b'a']
        content = (b'aa\tbb\tcc\n'
                   b'dd\tee\tff\n')
        # Warn on duplicates
        with open_infile(content) as inf:
            with pytest.warns(UserWarning, match='Duplicate field names: a'):
                reader = tsv.TsvReader(inf, fieldnames=fieldnames,
                                       duplicates='warn')
            asserts(reader, fieldnames)
        # Ignore duplicates
        with open_infile(content) as inf:
            reader = tsv.TsvReader(inf, fieldnames=fieldnames,
                                   duplicates='ignore')
            asserts(reader, fieldnames)
        # Raise error on duplicates
        with open_infile(content) as inf:
            with pytest.raises(ValueError, match='Duplicate field names: a'):
                reader = tsv.TsvReader(inf, fieldnames=fieldnames,
                                       duplicates='error')
