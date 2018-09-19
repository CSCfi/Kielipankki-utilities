#! /usr/bin/env python3
# -*- mode: Python; -*-


"""
Module scriptutil

Utility functions and a wrapper class for writing scripts, in
particular for filter scripts processing input and writing output.

Most of the code is taken from Jussi Piitulainen's scripts, either
directly or modified.
"""


import os
import re
import sys
import traceback

from argparse import ArgumentParser
from tempfile import mkstemp

import signal

# If the following are uncommented, the corresponding exception
# handlers are not reached in wrap_implement_main.
# signal.signal(signal.SIGINT, signal.SIG_DFL)
# signal.signal(signal.SIGPIPE, signal.SIG_DFL)


class BadData(Exception):
    """Exception for invalid data."""
    # stack trace is just noise
    pass


class BadCode(Exception):
    """Exception for code errors."""
    # this cannot happen
    pass


def get_argparser(argspecs=None, version='undefined', **kwargs):
    """Return an ArgumentParser with default and possibly other arguments.

    Construct an ArgumentParser with the default arguments infile,
    --out (-o), --in-place (-i), --backup (-b) and --version, and
    other arguments specified in `argspecs`.
    Arguments:
      `argspecs`: a list of command-line argument specifications; see
          `argparser_add_args` for the format
      `version`: the version string shown by --version.
      `**kwargs` is passed directly to `ArgumentParser`.
    """
    argparser = ArgumentParser(**kwargs)
    common_argspecs = [
        [
            # Before arguments in argspecs
            ('infiles = FILE /*',
             'input FILE (default: stdin)'),
        ],
        [
            # After arguments in argspecs
            ('--out -o = FILE -> outfile',
             'output FILE (default: stdout). FILE may be a template in which'
             ' the following strings are replaced with the corresponding'
             ' components of the input file name: {file} (file name), {dir}'
             ' (directory name) and {path} (directory and file name). With'
             ' a file name template, a separate output file is produced for'
             ' each input file; otherwise, the output for all input files is'
             ' combined into a single output file.'),
            ('--in-place -i -> inplace',
             'overwrite input file with output'),
            ('--backup -b = BAK',
             'keep input file with suffix BAK'),
            ('--version',
             'print {} and exit'.format(version)),
        ],
    ]
    argparser_add_args(
        argparser, common_argspecs[0] + (argspecs or []) + common_argspecs[1])
    return argparser


def argparser_add_args(argparser, argspecs):
    """Add the arguments specified in argspecs to ArgumentParser argparser.

    `argspecs` is a list of command-line argument specifications,
    which are lists or tuples of 2 or 3 elements: (argnames, help,
    [argdict]) where argnames is either a single string or a list or
    tuple of strings representing argument names (and optionally some
    options, see below), help is the usage string and argdict is a
    dictionary of the keyword arguments to be passed to
    `ArgumentParser.add_argument`. If argdict contains a default
    value, information about it is appended to the usage string,
    unless the usage string already contains the word "default".

    argnames (or its first element) is of the following form:
      argname (("|"|" ") argname)* ("=" metavar)? ("/" nargs)? ("->" dest)?.
    Each argname is an alternative name for the argument, and metavar,
    nargs and dest correspond to the keyword arguments of
    `ArgumentParser.add_argument` with the same names. The components
    may have spaces between them. If no metavar is specified and
    argdict has no action, add action='store_true'.
    """
    if argspecs:
        for argspec in argspecs:
            _argparser_add_arg(argparser, argspec)


def _argparser_add_arg(argparser, argspec):
    """Add the argument specified in argspec to ArgumentParser argparser.

    See `argparser_add_args` for the format of `argspec`.
    """
    if len(argspec) < 2:
        raise BadCode(
            'Argument specification needs at least name and help text')
    argnames, arghelp = argspec[:2]
    # Convert argnames to a list for futher processing
    if isinstance(argnames, str):
        argnames = [argnames]
    elif isinstance(argnames, tuple):
        argnames = list(argnames)
    argdict = (argspec[2] or {}) if len(argspec) > 2 else {}
    # Add information on the possible default value to the usage
    # message, unless it already contains the string "default".
    if 'default' in argdict and 'default' not in arghelp:
        arghelp += ' (default: %(default)s)'
    argdict['help'] = arghelp
    # Parse (the first element of) argnames
    mo = re.match(r"""(?P<names> [^=/>]+?)
                      (?: \s* = \s* (?P<metavar> \S+?)) ?
                      (?: \s* / \s* (?P<nargs> \S+?)) ?
                      (?: \s* -> \s* (?P<dest> \S+?)) ? $ """,
                  argnames[0], re.VERBOSE)
    if not mo:
        raise BadCode('Invalid argument specification string')
    argdict0 = dict((key, val) for key, val in mo.groupdict().items()
                    if val is not None)
    argnames[0:1] = re.split(r'\s*(?:\s+|\|)\s*', argdict0['names'].strip())
    del argdict0['names']
    argdict0.update(argdict)
    argdict = argdict0
    if 'metavar' not in argdict and 'action' not in argdict:
        argdict['action'] = 'store_true'
    # Split argument name by spaces and/or vertical bars
    argnames[0:1] = re.split(r'\s*(?:\s+|\|)\s*', argnames[0].strip())
    # If alternative option argument names omit the leading hyphens,
    # add them.
    isoptarg = (argnames[0][0] == '-')
    if isoptarg:
        for i in range(1, len(argnames)):
            if argnames[i][0] != '-':
                prefix = ('-' if len(argnames[i]) == 1 else '--')
                argnames[i] = prefix + argnames[i]
    argparser.add_argument(*argnames, **argdict)


def error_exit(*msg, progname=None):
    """Print message msg to standard error and exit with code 1.

    If progname is not None, prepend it to the error message.
    """
    print_error(*msg, progname=progname)
    exit(1)


def print_error(*msg, progname=None):
    """Print message msg to standard error.

    If progname is not None, prepend it to the error message.
    """
    if progname is not None:
        msg = (progname + ':',) + msg
    print(*msg, file=sys.stderr)


def get_args(argparser, unparsed_args=None, namespace=None,
             argcheck_fn=None, version=None):
    """Return the command-line arguments parsed with argparser.

    `unparsed_args` is a list of unparsed (command-line) arguments;
    the default is to use sys.argv. Parsed arguments are added to
    `namespace`; by default, they are added to a new empty Namespace.
    `argcheck_fn` is a function to check (and possibly modify) the
    parsed arguments, and `version` is the version to be printed when
    using the option --version.
    """
    args = argparser.parse_args(unparsed_args, namespace)
    if args.version:
        print(version)
        exit(0)
    if args.backup is not None:
        if '/' in args.backup:
            error_exit('usage: --backup suffix cannot contain /')
        if not args.backup:
            error_exit('usage: --backup suffix cannot be empty')
        if not args.inplace:
            error_exit('usage: --backup requires --in-place')
    if args.inplace:
        if args.infiles is None:
            error_exit('usage: --in-place requires input file(s)')
        if args.outfile is not None:
            error_exit('usage: --in-place not allowed with --out')
    if (args.outfile is not None) and os.path.exists(args.outfile):
        # easier to check this than that output file is different than
        # input file, though it be annoying when overwrite is wanted
        error_exit('usage: --out file must not exist')
    if callable(argcheck_fn):
        argcheck_fn(args)
    return args


class StdOutBuffer:

    """
    A context manager for sys.stdout.buffer, which does not close it at exit.

    Source: https://stackoverflow.com/a/40826961
    """

    def __enter__(self):
        return sys.stdout.buffer

    def __exit__(self, *args):
        pass


def wrap_main(main_fn, argparser, **getargs_kwargs):
    """Process arguments and call main with appropriate input and output.

    Process arguments with `argparser`, passing `**getargs_kwargs`
    to `get_args`, and then call `main_fn` with binary input and
    output, as specified in the arguments.
    """
    # TODO: Possibly support string or regex substitutions in file
    # name templates, e.g. {file:/foo/bar}.
    args = get_args(argparser, **getargs_kwargs)
    infile_count = len(args.infiles) if args.infiles else 0
    # Use StdOutBuffer() instead of sys.stdout.buffer directly, to
    # avoid closing stdout at the end of each with and so to avoid
    # having to make stdout a special case.
    stdout_buffer = StdOutBuffer()
    outfile_is_templ = args.outfile and '{' in args.outfile
    outfile = None if outfile_is_templ else args.outfile
    temp = None
    try:
        for infile_num, infile in enumerate(args.infiles or [None]):
            # infile is None if input from stdin
            # If the output is not a filename template, use a single
            # temp for output even for multiple input files
            if (args.inplace or (args.outfile is not None
                                 and (outfile_is_templ or infile_num == 0))):
                head, tail = os.path.split(infile
                                           if args.inplace or outfile_is_templ
                                           else outfile)
                if outfile_is_templ:
                    outfile = args.outfile.format(
                        path=infile, dir=head, file=tail, filename=tail)
                    if os.path.exists(outfile):
                        error_exit('usage: --out file must not exist: {}'
                                   .format(outfile))
                    head, tail = os.path.split(outfile)
                fd, temp = mkstemp(dir=head, prefix=tail)
                os.close(fd)
            # If the output file is a single file (and not a filename
            # template), for the first input file, overwrite the
            # output file; for the rest, append to it.
            outfile_mode = ('bw'
                            if not outfile_is_templ or infile_num == 0
                            else 'ba')
            with ((infile and open(infile, mode='br'))
                  or sys.stdin.buffer) as inf:
                with ((temp and open(temp, mode=outfile_mode))
                      or stdout_buffer) as ouf:
                    status = main_fn(inf, ouf)
            if args.backup:
                os.rename(infile, infile + args.backup)
            if args.inplace:
                os.rename(temp, infile)
            # For a non-template output filename, rename the output
            # file only if this was the last input file
            if outfile and (outfile_is_templ
                            or infile_num >= infile_count - 1):
                os.rename(temp, outfile)
            if status != 0:
                exit(status)
        exit(status)
    except IOError as exn:
        error_exit(exn)


def wrap_implement_main(implement_main_fn, *main_args, progname=None,
                        **main_kwargs):
    """Call the implementation of main and handle exceptions.

    Call `implement_main_fn` with `main_args` and `main_kwargs`.
    `progname` is the name of the program to be shown in error
    messages.
    """
    status = 1
    try:
        implement_main_fn(*main_args, **main_kwargs)
        status = 0
    except BadData as exn:
        print_error(exn, progname=progname)
    except BrokenPipeError as exn:
        print_error('in main thread: Broken Pipe', progname=progname)
    except KeyboardInterrupt as exn:
        print_error('in main thread: Keyboard Interrupt', progname=progname)
    except Exception as exn:
        print_error(traceback.format_exc(), progname=progname)
    return status


class InputProcessor:

    """
    An abstract class for a script processing input and writing output.

    A subclass must define at least the method `implement_main` and
    should re-define the class attributes VERSION and DESCRIPTION. The
    resulting script has the common arguments and options and it reads
    input and writes output in implement_main. In the simplest case,
    the code for running the script can be as follows:

      if __name__ == '__main__':
          InputProcessorSubclass().run()

    This class uses the functions defined above.
    """

    VERSION = 'unspecified'
    """Version information for the script"""
    DESCRIPTION = None
    """Description of the script to be shown in the usage message"""
    ARGSPECS = None
    """A list of argument specifications, which are pairs (argnames,
    argdict) where argnames is either a single string or a list of
    strings representing argument names and argdict is a dictionary of
    the keyword arguments to be passed to
    `ArgumentParser.add_argument`."""

    def __init__(self):
        """Initialize the class."""
        self.argparser = None
        """Argument parser"""
        self._args = None
        """Parsed command-line arguments"""
        self._progname = None
        """Program name"""

    def run(self, unparsed_args=None):
        """Process command-line arguments and run the main method."""
        if self.argparser is None:
            self.argparser = get_argparser(argspecs=self.ARGSPECS,
                                           version=self.VERSION,
                                           description=self.DESCRIPTION)
        self._progname = self.argparser.prog
        wrap_main(self.main, self.argparser, unparsed_args=unparsed_args,
                  argcheck_fn=self.check_args, version=self.VERSION)

    def check_args(self, args):
        """Check command-line arguments and assign them to self._args."""
        self._args = args

    def main(self, inf, ouf):
        """Call the implementation of main and handle exceptions."""
        return wrap_implement_main(
            self.implement_main, inf, ouf, progname=self._progname)

    def implement_main(self, *args, **kwargs):
        """The actual main method, to be implemented in a subclass."""
        pass

    def print_error(self, *msg):
        print_error(*msg, progname=self._progname)

    def error_exit(self, *msg):
        error_exit(*msg, progname=self._progname)
