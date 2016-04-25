# -*- coding: utf-8 -*-


"""
Module korpimport.util

Common utility functions and classes for Korp/CWB importing and VRT
processing scripts.
"""


import sys
import codecs
import errno
import string

from optparse import OptionParser


def elem_at(seq, index, default=None):
    """Return seq[elem] if it exists; otherwise default."""
    try:
        return seq[index]
    except IndexError:
        return default


def unique(lst):
    """Return the elements of list lst uniquified."""
    # This will be slow if the list is long, but for a short list this
    # might be as good as using a set. Another option might be an
    # ordered set.
    result = []
    for item in lst:
        if item not in result:
            result.append(item)
    return result


def whole_line_reader(stream, linebreak_chars=None):
    """Return whole lines from stream

    Return lines ending in one of linebreak_chars (default: newline
    \n), even if they may be split at other (Unicode) linebreak
    characters, such as NEL (\u0085).
    """
    linebreak_chars = linebreak_chars or u'\n'
    incompl_lines = []
    for line in stream:
        if line[-1] not in linebreak_chars:
            incompl_lines.append(line)
        elif incompl_lines:
            yield ''.join(incompl_lines) + line
            incompl_lines = []
        else:
            yield line
    if incompl_lines:
        yield ''.join(incompl_lines)


class PartialStringFormatter(string.Formatter):

    """
    A string formatter handling missing keys.

    A string formatter that outputs an empty (or other specified)
    string when a format key would cause a `KeyError` or
    `AttributeError`.

    Adapted from
    http://stackoverflow.com/questions/20248355/how-to-get-python-to-gracefully-format-none-and-non-existing-fields
    https://gist.github.com/navarroj/7689682
    """

    def __init__(self, missing=""):
        self.missing = missing

    def get_field(self, field_name, args, kwargs):
        # Handle missing fields
        try:
            return super(_PartialStringFormatter, self).get_field(
                field_name, args, kwargs)
        except (KeyError, AttributeError):
            return None, field_name

    def format_field(self, value, spec):
        if value is None:
            return self.missing
        else:
            return super(_PartialStringFormatter, self).format_field(
                value, spec)


def run(main, input_encoding='utf-8', output_encoding='utf-8', *args, **kwargs):
    """Run the main function; catch IOErrors and KeyboardInterrupt."""
    try:
        sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
        sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
        main(*args, **kwargs)
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


class Runner(object):

    """An abstract runner class wrapping the run function."""

    def __init__(self, input_encoding='utf-8', output_encoding='utf-8'):
        self._input_encoding = input_encoding
        self._output_encoding = output_encoding
        self._opts = self._args = None

    def run(self, *args, **kwargs):
        run(self.main, input_encoding=self._input_encoding,
            output_encoding=self._output_encoding, *args, **kwargs)

    def main(self):
        pass


class OptionRunner(Runner):

    """An abstract class for a script with options."""

    def __init__(self, args=None, **kwargs):
        super(OptionRunner, self).__init__(**kwargs)
        self.getopts(args)

    def getopts(self, args=None):
        pass

    def getopts_basic(self, optparser_args, args=None, *optlist):
        optparser = OptionParser(**optparser_args)
        if args is None:
            args = sys.argv[1:]
        if len(optlist) == 1 and isinstance(optlist[0], list):
            optlist = optlist[0]
        for optspec in optlist:
            if isinstance(optspec[-1], dict):
                optnames = optspec[:-1]
                optopts = optspec[-1]
            else:
                optnames = optspec
                optopts = {}
            optparser.add_option(*optnames, **optopts)
        self._opts, self._args = optparser.parse_args(args)


class InputProcessor(OptionRunner):

    """An abstract class for a script processing input."""

    def __init__(self, args=None, **kwargs):
        super(InputProcessor, self).__init__(args, **kwargs)

    def process_input(self, args):
        if isinstance(args, list):
            for arg in args:
                self.process_input(arg)
        elif isinstance(args, basestring):
            with codecs.open(args, 'r', encoding=self._input_encoding) as f:
                self.process_input_stream(f, args)
        else:
            self.process_input_stream(args)

    def process_input_stream(self, stream, filename=None):
        pass

    def main(self):
        self.process_input(self._args or sys.stdin)
