
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


@pytest.fixture
def fieldnames_abc():
    """Fixture returning field names (a, b, c)."""
    yield [b'a', b'b', b'c']


@pytest.fixture
def fieldnames_aba():
    """Fixture returning field names containing a duplicate (a, b, a)."""
    yield [b'a', b'b', b'a']


@pytest.fixture
def content_base():
    """Fixture returning basic two-line, three-field TSV content."""
    yield (b'aa\tbb\tcc\n'
           b'dd\tee\tff\n')


@pytest.fixture
def content_abc(fieldnames_abc, content_base):
    """Fixture returning field names (a, b, c) and three content lines."""
    yield b'\t'.join(fieldnames_abc) + b'\n' + content_base


@pytest.fixture
def content_aba(fieldnames_aba, content_base):
    """Fixture returning field names (a, b, a) and three content lines."""
    yield b'\t'.join(fieldnames_aba) + b'\n' + content_base


@pytest.fixture
def content_abc_entities(fieldnames_abc):
    """Fixture returning field names and content with chars to be encoded.

    Returns a list of lines.
    """
    yield [b'\t'.join(fieldnames_abc) + b'\n',
           b'"\tb<\t>c&\n',
           # Already-encoded entities
           b'a&lt;b\te&gt;e\tf&quot;f&amp;\n']


@pytest.fixture
def content_abc_entities_joined(content_abc_entities):
    """Fixture returning content with entities, joined to a single bytes."""
    return b''.join(content_abc_entities)


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

    def test_fieldnames_arg(self, open_infile, fieldnames_abc, content_base):
        """Test `TsvReader` with field names as an argument."""
        with open_infile(content_base) as inf:
            reader = tsv.TsvReader(inf, fieldnames=fieldnames_abc)
            # Also test TsvReader.read_fieldnames()
            assert reader.read_fieldnames() == fieldnames_abc
            self._test_tsv_content(reader, fieldnames_abc, content_base)

    def test_fieldnames_arg_empty(self, open_infile, fieldnames_abc):
        """Test `TsvReader`, field names as argument, empty input file."""
        content = b''
        with open_infile(content) as inf:
            reader = tsv.TsvReader(inf, fieldnames=fieldnames_abc)
            assert reader.read_fieldnames() == fieldnames_abc
            with pytest.raises(StopIteration):
                d = next(reader)

    def test_fieldnames_heading_row(self, open_infile, fieldnames_abc,
                                    content_abc):
        """Test `TsvReader` with field names in a heading row."""
        with open_infile(content_abc) as inf:
            reader = tsv.TsvReader(inf)
            self._test_tsv_content(reader, fieldnames_abc, content_abc, True)

    def test_fieldnames_heading_row_empty(self, open_infile, fieldnames_abc):
        """Test `TsvReader`, field names in a heading row, empty rest."""
        content = b'a\tb\tc\n'
        with open_infile(content) as inf:
            reader = tsv.TsvReader(inf)
            with pytest.raises(StopIteration):
                d = next(reader)
            assert reader.fieldnames == fieldnames_abc

    def test_read_fieldnames(self, open_infile, fieldnames_abc, content_abc):
        """Test `TsvReader.read_fieldnames`."""
        with open_infile(content_abc) as inf:
            reader = tsv.TsvReader(inf)
            assert reader.read_fieldnames() == fieldnames_abc
            self._test_tsv_content(reader, fieldnames_abc, content_abc, True)

    def test_encode_entities_always(self, open_infile, fieldnames_abc,
                                    content_abc_entities,
                                    content_abc_entities_joined):
        """Test `TsvReader` always encoding entities."""
        content_enc = [escape(line) for line in content_abc_entities]
        # Always encoding entities
        for entities in [None, tsv.EncodeEntities.ALWAYS]:
            with open_infile(content_abc_entities_joined) as inf:
                reader = tsv.TsvReader(inf, entities=entities)
                assert reader.read_fieldnames() == fieldnames_abc
                self._test_tsv_content(
                    reader, fieldnames_abc, content_enc, True)

    def test_encode_entities_non_entities(self, open_infile, fieldnames_abc,
                                          content_abc_entities,
                                          content_abc_entities_joined):
        """Test `TsvReader` encoding entities but no & in existing ones."""
        content_enc = [content_abc_entities[0], escape(content_abc_entities[1]),
                       content_abc_entities[2]]
        with open_infile(content_abc_entities_joined) as inf:
            reader = tsv.TsvReader(
                inf, entities=tsv.EncodeEntities.NON_ENTITIES)
            assert reader.read_fieldnames() == fieldnames_abc
            self._test_tsv_content(reader, fieldnames_abc, content_enc, True)

    def test_encode_entities_never(self, open_infile, fieldnames_abc,
                                   content_abc_entities,
                                   content_abc_entities_joined):
        """Test `TsvReader` never encoding entities."""
        with open_infile(content_abc_entities_joined) as inf:
            reader = tsv.TsvReader(inf, entities=tsv.EncodeEntities.NEVER)
            assert reader.read_fieldnames() == fieldnames_abc
            self._test_tsv_content(
                reader, fieldnames_abc, content_abc_entities, True)

    def _duplicate_fieldnames_asserts(self, reader, fieldnames):
        """Common assertions for duplicate fieldnames tests."""
        # If next() is called only after read_fieldnames, pytest.warns
        # and pytest.raises do not seem to report catch the warning
        # and error
        fields = next(reader)
        assert reader.read_fieldnames() == fieldnames
        assert fields[b'a'] == b'cc'
        assert fields[b'b'] == b'bb'

    def _handle_duplicates_base(self, inf, fieldnames, fieldnames_dupl,
                                dupl_mode='ignore'):
        """Call `self._duplicate_fieldnames_asserts` for a TSV reader.

        `inf is an open TSV file to read, `fieldnames` the
        `fieldnames` argument to pass to `TsvReader`,
        `fieldnames_dupl` field names containing a duplicate and
        `dupl_mode` the mode for handling duplicate field names.
        """
        reader = tsv.TsvReader(inf, fieldnames=fieldnames, duplicates=dupl_mode)
        self._duplicate_fieldnames_asserts(reader, fieldnames_dupl)

    def _handle_duplicates_warn(self, *args):
        """Check that reading duplicate field names causes a warning."""
        with pytest.warns(UserWarning, match='Duplicate field names: a$'):
            self._handle_duplicates_base(*args, dupl_mode='warn')

    def _handle_duplicates_error(self, *args):
        """Check that reading duplicate field names raises an error."""
        with pytest.raises(ValueError, match='Duplicate field names: a$'):
            self._handle_duplicates_base(*args, dupl_mode='error')

    @pytest.mark.parametrize(
        # Parametrize whether to ignore, warn on or raise error on
        # duplicate field names
        'handle_func',
        [
            _handle_duplicates_base,
            _handle_duplicates_warn,
            _handle_duplicates_error,
        ]
    )
    @pytest.mark.parametrize(
        # Parametrize the content fixture (containing or not
        # containing field names) and whether fieldnames should be
        # explicitly specified
        'content_fixt,explicit_fieldnames',
        [
            ('content_base', True),
            ('content_aba', False),
        ]
    )
    def test_duplicate_fieldnames(self, handle_func,
                                  content_fixt, explicit_fieldnames,
                                  open_infile, fieldnames_aba, request):
        """Test handling duplicate fieldnames.

        `handle_func` is the function (method) to be used for testing
        (using a certain mode of handling duplicates), `content_fixt`
        the name of the fixture providing TSV content, and
        `explicit_fieldnames` a Boolean specifying whether fieldnames
        should be explicitly passed to TsvReader.
        """
        fieldnames = fieldnames_aba if explicit_fieldnames else None
        with open_infile(request.getfixturevalue(content_fixt)) as inf:
            handle_func(self, inf, fieldnames, fieldnames_aba)
