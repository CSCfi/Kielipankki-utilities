#! /usr/bin/env python3
# -*- mode: Python; -*-


"""
Module korpimport.scriptutil

Common utility functions and classes for input processing scripts.

This is contains part of util.py converted to or reimplemented for
Python 3(.4).
"""


import errno
import io
import os.path
import sys

# CHECK: Is the following an appropriate way of specifying where
# vrtargsoolib can be found, as it is in ../../vrt-tools relative to
# this module (in the repository)?
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../../vrt-tools')))
import vrtargsoolib


DEFAULT_INPUT_ENCODING = 'UTF-8'
DEFAULT_OUTPUT_ENCODING = 'UTF-8'


def _reconfigure_stream(stream, **kwargs):
    for param in ['encoding', 'errors', 'line_buffering', 'write_through']:
        try:
            # Attribute write_through is new in Python 3.7
            kwargs[param] = kwargs.get(param) or getattr(stream, param)
        except AttributeError as e:
            pass
    return io.TextIOWrapper(stream.buffer, **kwargs)


def run(main, input_encoding=DEFAULT_INPUT_ENCODING,
        output_encoding=DEFAULT_OUTPUT_ENCODING,
        *args, **kwargs):
    """Run the main function; catch IOErrors and KeyboardInterrupt."""
    try:
        # CHECK: Is specifying encodings useful?
        if input_encoding:
            sys.stdin = _reconfigure_stream(sys.stdin, encoding=input_encoding)
        if output_encoding:
            sys.stdout = _reconfigure_stream(sys.stdout,
                                             encoding=output_encoding)
            sys.stderr = _reconfigure_stream(sys.stderr,
                                             encoding=output_encoding)
        main(*args, **kwargs)
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


class Runner(object):

    """
    An abstract runner class wrapping the run function.

    Also includes methods to write error and warning messages and to
    write to output (sys.stdout).
    """

    def __init__(self, **kwargs):
        # Call super to allow use in multiple inheritance
        super().__init__()
        # CHECK: Is specifying encodings useful?
        self._input_encoding = kwargs.get('input_encoding',
                                          DEFAULT_INPUT_ENCODING)
        self._output_encoding = kwargs.get('output_encoding',
                                           DEFAULT_OUTPUT_ENCODING)
        self._args = None

    def run(self, *args, **kwargs):
        run(self.main, input_encoding=self._input_encoding,
            output_encoding=self._output_encoding, *args, **kwargs)

    def main(self):
        pass

    def write_message(self, message, outstream=None, filename=None,
                      linenr=None, show_fileinfo=True, **kwargs):
        outstream = outstream or sys.stderr
        if show_fileinfo and filename is not None:
            loc_info = (' (' + filename + (':' + str(linenr) if linenr else '')
                        + ')')
        else:
            loc_info = ''
        outstream.write(message + loc_info + '\n')

    def error(self, message, exitcode=1, **kwargs):
        self.write_message('Error: ' + message, **kwargs)
        exit(exitcode)

    def warn(self, message, **kwargs):
        self.write_message('Warning: ' + message, **kwargs)

    def output(self, line):
        sys.stdout.write(line)


class ArgumentRunner(Runner, vrtargsoolib.BasicProcessor):

    """An abstract class for a script with arguments."""

    class OPTIONS(vrtargsoolib.BasicProcessor.OPTIONS):
        common_args = vrtargsoolib.CommonArgs.none

    def __init__(self, args=None, **kwargs):
        # FIXME: This does not pass any encoding arguments to the
        # superclass __init__, as the **kwargs as passed to
        # _get_argparser should contain only keyword arguments
        # recognized by argparse.ArgumentParser().
        super().__init__()
        self._get_argparser(**kwargs)
        self._args = self._argparser.parse_args(args)
        self.check_args(self._args)


class InputProcessor(vrtargsoolib.InputProcessor):

    """An abstract class for a script processing input."""

    class OPTIONS(vrtargsoolib.InputProcessor.OPTIONS):
        common_args = vrtargsoolib.CommonArgs.none

    def __init__(self):
        """Initialize the class."""
        super().__init__()
