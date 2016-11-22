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
import csv
import re
import os

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


def _tsv_stream_dictreader(stream, utf8_input=False, *args, **kwargs):
    """Return a reader for TSV files, yield values in Unicode."""

    def utf8_encoder(unicode_csv_data):
        for line in unicode_csv_data:
            yield line.encode('utf-8')

    kwargs.update(dict(delimiter='\t', quoting=csv.QUOTE_NONE))
    # print "tsv stream", repr(stream)
    if not utf8_input:
        # print "encode to utf8"
        stream = utf8_encoder(stream)
    reader = csv.DictReader(stream, *args, **kwargs)
    for row in reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield dict((key, unicode(val, 'utf-8'))
                   for key, val in row.iteritems())


def tsv_dictreader(stream_or_fname, *args, **kwargs):
    """Return a reader for a TSV stream or file to yield values in Unicode."""
    if isinstance(stream_or_fname, basestring):
        with open(stream_or_fname, 'rb') as stream:
            for line in _tsv_stream_dictreader(
                    stream, *args, utf8_input=True, **kwargs):
                yield line
    else:
        for line in _tsv_stream_dictreader(stream_or_fname, *args, **kwargs):
            # print line
            yield line


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


def subst_var_refs(str_, vardict=None):
    """Substitute variable references in `str_` with values in `vardict`.

    Substitute variable references of the kind ``$var`` and ``${var}``
    with the value `vardict['var']`. If the key `'var'` is not in
    `vardict`, replace the reference with an empty string. If
    `vardict` is not specified, use `os.environ`.
    """
    vardict = vardict or os.environ

    def get_envvar(matchobj):
        return vardict.get(matchobj.group(1).strip('{}'), '')

    return re.sub(r'\$(\{.+?\}|\w+)', get_envvar, str_)


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
        if input_encoding:
            sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
        if output_encoding:
            sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
            sys.stderr = codecs.getwriter(output_encoding)(sys.stderr)
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

    """
    An abstract runner class wrapping the run function.

    Also includes methods to write error and warning messages and to
    write to output (sys.stdout).
    """

    def __init__(self, input_encoding='utf-8', output_encoding='utf-8'):
        self._input_encoding = input_encoding
        self._output_encoding = output_encoding
        self._opts = self._args = None

    def run(self, *args, **kwargs):
        run(self.main, input_encoding=self._input_encoding,
            output_encoding=self._output_encoding, *args, **kwargs)

    def main(self):
        pass

    def write_message(self, message, outstream=None, filename=None,
                      linenr=None, **kwargs):
        outstream = outstream or sys.stderr
        if filename is not None:
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


class OptionRunner(Runner):

    """An abstract class for a script with options."""

    def __init__(self, args=None, **kwargs):
        super(OptionRunner, self).__init__(**kwargs)
        self.getopts(args)

    def getopts(self, args=None):
        pass

    def getopts_basic(self, optparser_args, args=None, *optlist):
        """Get command-line options using optparse.

        The arguments in `optlist` correspond to the arguments to
        `OptionParser.add_option`: option names followed by a
        dictionary corresponding to the keyword argumnets. The iniial
        dashes in option names are optional. If only one option name
        argument is present, it is split by spaces, commas and
        vertical bars to get the actual option names. In addition, the
        value for the `add_option` keyword argument `metavar` may be
        specified after an equals sign following the option names. A
        missing `metavar` does *not* indicate that the option has no
        argument.
        """
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
            if len(optnames) == 1:
                optnames = re.split(r'\s*=\s*', optnames[0])
                if len(optnames) == 2:
                    optopts['metavar'] = optnames[1]
                optnames = re.split(r'\s*[\s,|]\s*', optnames[0])
            for optnamenum, optname in enumerate(optnames):
                if optname[0] != '-':
                    optnames[optnamenum] = (
                        ('-' if len(optname) == 1 else '--') + optname)
            optparser.add_option(*optnames, **optopts)
        self._opts, self._args = optparser.parse_args(args)


class BasicInputProcessor(Runner):

    """An abstract class for a script processing input."""

    def __init__(self, args=None, **kwargs):
        super(BasicInputProcessor, self).__init__(args, **kwargs)
        self._linenr = 0
        self._filename = None
        # FIXME: These are not yet the codecs versions, since they are
        # initialized only in the run function
        self._error_stream = sys.stderr
        self._output_stream = sys.stdout

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

    def write_message(self, message, outstream=None, filename=None,
                      linenr=None, **kwargs):
        filename = filename or self._filename or '<stdin>'
        linenr = linenr or self._linenr
        super(BasicInputProcessor, self).write_message(
            message, outstream=outstream, filename=filename, linenr=linenr,
            **kwargs)

    def main(self):
        self.process_input(self._args or sys.stdin)


class InputProcessor(BasicInputProcessor, OptionRunner):

    """An abstract class for a script processing input and with options."""

    def __init__(self, args=None, **kwargs):
        super(InputProcessor, self).__init__(args, **kwargs)
