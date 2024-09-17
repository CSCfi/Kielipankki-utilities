
"""
Module libvrt.seekable

This module contains function get_seekable making a non-seekable input
file, such as standard input, appear seekable by using a wrapper
object that copies the contents of the file to a temporary file.
"""


import os
import sys

from tempfile import NamedTemporaryFile


def get_seekable(infile):
    """If `infile` is not seekable, return a wrapper making it appear such.

    Also return a wrapper if the name of infile is ``<stdin>``.
    If `infile` is seekable, return it as is.
    """
    # In some cases, seekable() would seem to return True for stdin,
    # so also test for name "<stdin>".
    if infile.seekable() and infile.name != '<stdin>':
        return infile
    else:
        return _SeekableInput(infile)


class _SeekableInput:

    """
    A wrapper class making an unseekable input file (such as stdin)
    appear seekable by capturing its contents to a temporary file and
    accessing the latter after a `seek()` call.
    """

    def __init__(self, infile):
        """Create object with `infile` as the unseekable base file."""
        # self._infile is initially the base file, but changed to the
        # capture file after a seek()
        self._infile = infile
        # Information on infile for the capture file
        self.mode = self._infile.mode
        # encoding and newline are not available for binary files
        self.encoding = getattr(self._infile, 'encoding', None)
        self.newline = getattr(self._infile, 'newline', None)
        # This is not exact: could we somehow get the information on
        # the value of buffering for infile?
        if type(infile).__name__ == 'FileIO':
            # No buffering
            self._buffering = 0
        else:
            # The default
            self._buffering = -1
        # The temporary file to which infile contents are copied
        self._capture_file = self._open_capture_file_write()
        self._capture_filename = self._capture_file.name
        self._capturing = True

    def __getattr__(self, name):
        """Return attribute `name`."""
        # Access attribute of the base file if not defined here
        return getattr(self._infile, name)

    def __iter__(self):
        """Return iterator (this object)."""
        return self

    def __next__(self):
        """Return the next line."""
        return self._capturing_read('__next__')

    def __enter__(self):
        """Enter runtime context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit runtime context."""
        # Exit the context of the input file
        self._infile.__exit__(exc_type, exc_value, traceback)
        if self._capturing:
            # Exit the context of the capture file
            self._capture_file.__exit__(exc_type, exc_value, traceback)
        # Remove the capture file
        os.remove(self._capture_filename)
        return False

    def readline(self, *args):
        """Read line from input."""
        return self._capturing_read('readline', *args)

    def readlines(self, *args):
        """Read lines from input."""
        return self._capturing_read('readlines', *args,
                                    write_func=self._capture_file.writelines)

    def read(self, *args):
        """Read from input."""
        return self._capturing_read('read', *args)

    def seekable(self):
        """This file is seekable."""
        return True

    def seek(self, *args):
        """Seek file according to `args`."""
        # If capturing, capture the rest of the input if needed and
        # change self._infile to point to the capture file
        if self._capturing:
            self._capture_rest()
        return self._infile.seek(*args)

    def _capturing_read(self, method_name, *args, write_func=None):
        """Read from `self._infile` and write to capture file if capturing.

        Read using from `self._infile` by calling method `method_name`
        with arguments `*args`. In addition to returning the value,
        write it to the capture file if capturing. If `write_func` is
        not `None`, write the read data to the capture file using it,
        otherwise with `write`.
        """
        value = getattr(self._infile, method_name)(*args)
        if write_func is None:
            write_func = self._capture_file.write
        if self._capturing:
            write_func(value)
        return value

    def _capture_rest(self):
        """If capturing, capture the rest of the input if needed.

        Also change `self._infile` to point to the capture file opened
        for reading.
        """
        if self._capturing:
            for line in self._infile:
                self._capture_file.write(line)
            # __exit__() closes the file
            self._capture_file.__exit__(None, None, None)
            self._capturing = False
            self._infile = self._open_capture_file_read()

    def _open_capture_file_write(self):
        """Open the capture file for writing."""
        mode = self.mode.replace('r', 'w')
        capture_file = NamedTemporaryFile(
            mode=mode, buffering=self._buffering, encoding=self.encoding,
            newline=self.newline, delete=False)
        capture_file.__enter__()
        return capture_file

    def _open_capture_file_read(self):
        """Open the capture file for reading."""
        f = open(self._capture_filename, mode=self.mode,
                 buffering=self._buffering, encoding=self.encoding,
                 newline=self.newline)
        f.__enter__()
        return f
