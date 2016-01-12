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

    
class InputProcessor(Runner):

    """An abstract class for a script processing input."""

    def __init__(self, args=None, **kwargs):
        super(InputProcessor, self).__init__(**kwargs)
        self.getopts(args)

    def process_input(self, args):
        if isinstance(args, list):
            for arg in args:
                self.process_input(arg)
        elif isinstance(args, basestring):
            with codecs.open(args, 'r', encoding='utf-8') as f:
                self.process_input_stream(f, args)
        else:
            self.process_input_stream(args)

    def process_input_stream(self, stream, filename=None):
        pass

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

    def main(self):
        self.process_input(self._args or sys.stdin)
