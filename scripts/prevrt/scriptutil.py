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
      `argspecs`: a list of argument specifications, which are pairs
          (argnames, argdict) where argnames is either a single string
          or a list of strings representing argument names and argdict
          is a dictionary of the keyword arguments to be passed to
          `ArgumentParser.add_argument`.
      `version`: the version string shown by --version.
      `**kwargs` is passed directly to `ArgumentParser`.
    """
    argparser = ArgumentParser(**kwargs)
    common_argspecs = [
        ('infile',
         dict(nargs='?', metavar='file',
              help='input file (default stdin)')),
        (['--out', '-o'],
         dict(dest='outfile', metavar='file',
              help='output file (default stdout)')),
        (['--in-place', '-i'],
         dict(dest='inplace', action='store_true',
              help='overwrite input file with output')),
        (['--backup', '-b'],
         dict(metavar='bak',
              help='keep input file with suffix bak')),
        (['--version'],
         dict(action='store_true',
              help='print {} and exit'.format(version))),
    ]
    argparser_add_args(argparser, common_argspecs)
    argparser_add_args(argparser, argspecs)
    return argparser


def argparser_add_args(argparser, argspecs):
    """Add the arguments specified in argspecs to ArgumentParser argparser."""
    if argspecs:
        for argnames, argdict in argspecs:
            if not isinstance(argnames, list):
                argnames = [argnames]
            argparser.add_argument(*argnames, **(argdict or {}))


def error_exit(*msg):
    """Print message msg to standard error and exit with code 1."""
    print_error(*msg)
    exit(1)


def print_error(*msg):
    """Print message msg to standard error."""
    print(*msg, file=sys.stderr)


def get_args(argparser, argcheck_fn=None, version=None):
    """Return the command-line arguments parsed with argparser.

    `argcheck_fn` is a function to check (and possibly modify) the
    parsed arguments, and `version` is the version to be printed when
    using the option --version.
    """
    args = argparser.parse_args()
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
        if args.infile is None:
            error_exit('usage: --in-place requires input file')
        if args.outfile is not None:
            error_exit('usage: --in-place not allowed with --out')
    if (args.outfile is not None) and os.path.exists(args.outfile):
        # easier to check this than that output file is different than
        # input file, though it be annoying when overwrite is wanted
        error_exit('usage: --out file must not exist')
    if callable(argcheck_fn):
        argcheck_fn(args)
    return args


def wrap_main(main_fn, argparser, argcheck_fn=None, version=None):
    """Process arguments and call main with appropriate input and output.

    Process arguments with `argparser`, passing `argcheck_fn` and
    `version` to `get_args`, and then call `main_fn` with binary input
    and output, as specified in the arguments.
    """
    args = get_args(argparser, argcheck_fn, version)
    try:
        if args.inplace or (args.outfile is not None):
            head, tail = os.path.split(args.infile
                                       if args.inplace
                                       else args.outfile)
            fd, temp = mkstemp(dir=head, prefix=tail)
            os.close(fd)
        else:
            temp = None
        with ((args.infile and open(args.infile, mode='br'))
              or sys.stdin.buffer) as inf:
            with ((temp and open(temp, mode='bw'))
                  or sys.stdout.buffer) as ouf:
                status = main_fn(inf, ouf)
        if args.backup:
            os.rename(args.infile, args.infile + args.backup)
        if args.inplace:
            os.rename(temp, args.infile)
        if args.outfile:
            os.rename(temp, args.outfile)
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
    msg_prefix = str(progname) + ':'
    try:
        implement_main_fn(*main_args, **main_kwargs)
        status = 0
    except BadData as exn:
        print_error(msg_prefix, exn)
    except BrokenPipeError as exn:
        print_error(msg_prefix, 'in main thread: Broken Pipe')
    except KeyboardInterrupt as exn:
        print_error(msg_prefix, 'in main thread: Keyboard Interrupt')
    except Exception as exn:
        print_error(traceback.format_exc())
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
        self.argparser = get_argparser(argspecs=self.ARGSPECS,
                                       version=self.VERSION,
                                       description=self.DESCRIPTION)
        """Argument parser"""
        self._args = None
        """Parsed command-line arguments"""

    def run(self):
        """Process command-line arguments and run the main method."""
        wrap_main(self.main, self.argparser, self.check_args,
                  version=self.VERSION)

    def check_args(self, args):
        """Check command-line arguments and assign them to self._args."""
        self._args = args

    def main(self, inf, ouf):
        """Call the implementation of main and handle exceptions."""
        wrap_implement_main(
            self.implement_main, inf, ouf, progname=self.argparser.prog)

    def implement_main(self, *args, **kwargs):
        """The actual main method, to be implemented in a subclass."""
        pass
