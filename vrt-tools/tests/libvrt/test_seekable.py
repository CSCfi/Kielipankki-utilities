
"""
test_seekable.py

Pytest tests for libvrt.seekable.
"""


import os
import os.path
import sys

import pytest

from tempfile import NamedTemporaryFile
from io import UnsupportedOperation

from libvrt.seekable import get_seekable, _SeekableInput


# Input content as strings and bytes
_filedata = [f'line {i}\n' for i in range(10)]
_filedata_bytes = [line.encode('utf-8') for line in _filedata]


def readfile(filename):
    """Return the contents of file `filename`."""
    with open(filename, 'r') as f:
        return f.readlines()


@pytest.fixture
def infile():
    """Fixture creating temporary file with content `_filedata`.

    Returns the name of the temporary file.
    Removes the file at teardown.
    """
    with NamedTemporaryFile('w', delete=False) as ntf:
        ntf.writelines(_filedata)
    yield ntf.name
    os.remove(ntf.name)


@pytest.fixture
def open_infile(infile):
    """Fixture as factory yielding a function to open `infile`.

    The factory function takes as its arguments positional and keyword
    arguments to `open` and returns the opened file object.
    """

    # Opened files
    files = []

    def _open_infile(*args, **kwargs):
        """Return opened `infile`, `*args` and `**kwargs` passed to `open`."""
        file_ = open(infile, *args, **kwargs)
        files.append(file_)
        file_.__enter__()
        return file_

    yield _open_infile

    # Cleanup: close opened files
    for file_ in files:
        file_.__exit__(None, None, None)


@pytest.fixture
def open_infile_unseekable(open_infile, monkeypatch):
    """Fixture as factory: yield function returning `open_infile` unseekable.

    Monkey-pathces the file returned by `open_infile` to appear
    unseekable: The methods `seekable` and `seek` of the returned file
    object are replaced with ones making the object appear unseekable.
    """

    def _open_infile_unseekable(*args, **kwargs):
        """Return open input file, `*args` and `**kwargs` passed to `open`."""

        def _unsupported_seek(*args):
            """`seek` replacement raising `io.UnsupportedOperation`."""
            raise UnsupportedOperation()

        file_ = open_infile(*args, **kwargs)
        monkeypatch.setattr(file_, 'seekable', lambda: False)
        monkeypatch.setattr(file_, 'seek', _unsupported_seek)
        return file_

    yield _open_infile_unseekable


@pytest.fixture
def open_infile_seekable(open_infile_unseekable):
    """Fixture as factory: yield function returning seekable input file.

    Yields a function returning a seekable input file, created by
    calling `seekable.get_seekable` on the one returned by
    `open_infile_unseekable`.
    """

    def _open_infile_seekable(*args, **kwargs):
        """Return open input file with `*args` and `**kwargs` to `open`."""
        return get_seekable(open_infile_unseekable(*args, **kwargs))

    yield _open_infile_seekable


@pytest.fixture
def capture_file_after_read_seek(open_infile_seekable):
    """Fixture as factory: yield function reading from input file after seek.

    Yields a function that opens a seekable input file with given
    arguments, reads from it with a given function (taking the input
    file object as the argument), seeks to the beginning, checks that
    the content of the captured file is the same as that of the input
    file and returns the read value.
    """

    def _capture_file_after_read_seek(readfunc, *args, **kwargs):
        """Return value read by `readfunc`; `*args`, `**kwargs` to `open`."""
        with open_infile_seekable(*args, **kwargs) as f:
            captfile = f._capture_filename
            readval = readfunc(f)
            f.seek(0)
            assert readfile(captfile) == _filedata
            return readval

    yield _capture_file_after_read_seek


class TestGetSeekable:

    """Tests for `get_seekable()`."""

    def test_seekable_arg(self, open_infile):
        """Test `get_seekable` for a seekable argument: returned as is."""
        f = open_infile('r')
        assert f.seekable()
        assert get_seekable(f) == f

    def test_unseekable_arg(self, open_infile_unseekable):
        """Test `get_seekable` for an unseekable argument."""
        f = open_infile_unseekable('r')
        sf = get_seekable(f)
        assert not f.seekable()
        assert sf != f
        assert type(sf) == _SeekableInput
        assert sf.seekable()

    @pytest.mark.parametrize(
        # open *args, open **kwargs, result read from file
        'open_args,open_kwargs,result', [
            (['r'], {}, _filedata),
            (['rb'], {}, _filedata_bytes),
            (['rb'], {'buffering': 0}, _filedata_bytes),
        ]
    )
    def test_iter(self, open_args, open_kwargs, result,
                  open_infile_seekable):
        """Test reading from wrapped seekable file with an iterator."""
        f = open_infile_seekable(*open_args, **open_kwargs)
        lines = [line for line in f]
        assert lines == result

    def test_capturefile_removed(self, open_infile_seekable):
        """Test that `_SeekableInput` capture file removed at context exit."""
        with open_infile_seekable('r') as f:
            captfile = f._capture_filename
            lines = [line for line in f]
            assert os.path.isfile(captfile)
        assert not os.path.isfile(captfile)

    def test_seek(self, open_infile_seekable):
        """Test seeking to the beginning of a seekable input file."""
        with open_infile_seekable('r') as f:
            captfile = f._capture_filename
            assert readfile(captfile) == []
            f.seek(0)
            assert readfile(captfile) == _filedata

    def test_seek_multi(self, open_infile_seekable):
        """Test seeking a seekable input file multiple times."""
        with open_infile_seekable('r') as f:
            for i in range(5):
                lines = f.readlines()
                f.seek(0)
                assert lines == _filedata

    @pytest.mark.parametrize(
        # Parameters: open *args, open **kwargs, base result
        'open_args,open_kwargs,base_result', [
            (['r'], {}, _filedata),
            (['rb'], {}, _filedata_bytes),
            (['rb'], {'buffering': 0}, _filedata_bytes),
        ]
    )
    @pytest.mark.parametrize(
        # Parameters: function with which to read from file, taking
        # the file object as argument (passed to
        # capture_file_after_read_seek); function taking base result
        # as the argument and returning the final result
        'readfunc,resultfunc', [
            (lambda f: [ln for ln in f], lambda r: r),
            (lambda f: f.readlines(), lambda r: r),
            (lambda f: f.readline(), lambda r: r[0]),
            (lambda f: f.read(5), lambda r: r[0][:5]),
        ]
    )
    def test_read_seek(self, open_args, open_kwargs, base_result,
                       readfunc, resultfunc,
                       capture_file_after_read_seek):
        """Test seeking (and content of capture file) after reading."""
        assert (
            capture_file_after_read_seek(readfunc, *open_args, **open_kwargs)
            == resultfunc(base_result)
        )

    def test_attr_passthrough(self, open_infile_seekable):
        """Test that methods not defined in _SeekableInput are pass through.

        The methods are passed through to the wrapped file.
        """
        with open_infile_seekable('r') as f:
            assert not f.isatty()
            assert f.readable()
            assert not f.writable()
            assert not f.closed
            assert f.name
