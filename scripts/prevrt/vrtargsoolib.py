#! /usr/bin/env python3
# -*- mode: Python; -*-


"""
Module vrtargsoolib

Utility functions and a wrapper class for writing scripts, in
particular for filter scripts processing input and writing output.

The code wraps functions in vrtargslib.
"""


import re
import sys

import vrtargslib


def get_argparser(argspecs=None, *, common_trans_args=True, **kwargs):
    """Return an ArgumentParser with common and possibly other arguments.

    Return an `ArgumentParser` with common arguments by calling
    `vrtargslib.trans_args` (or `vrtargslib.version_args`); see their
    documentation for information on the common arguments.
    Arguments:
      `argspecs`: a list of command-line argument specifications in
          addition to the common ones; see `argparser_add_args` for
          the format
      `common_trans_args`: add the common arguments for transforming
          scripts; if `False`, only add --version
      `**kwargs` is passed to `vrtargslib.trans_args` (or
          `vrtargslib.version_args`) and should contain at least a
          `description` and possibly `inplace=False`, if the
          --in-place argument is not requested.
    """
    argparser = (vrtargslib.trans_args(**kwargs)
                 if common_trans_args else
                 vrtargslib.version_args(
                     description=kwargs.get('description')))
    if argspecs:
        argparser_add_args(argparser, argspecs)
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
        raise vrtargslib.BadCode(
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
        raise vrtargslib.BadCode('Invalid argument specification string')
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
             argcheck_fn=None, **kwargs):
    """Return the command-line arguments parsed with argparser.

    `unparsed_args` is a list of unparsed (command-line) arguments;
    the default is to use sys.argv. Parsed arguments are added to
    `namespace`; by default, they are added to a new empty Namespace.
    `argcheck_fn` is a function to check (and possibly modify) the
    parsed arguments. `**kwargs` is only to allow unhandled keyword
    arguments.
    """
    # Default values for undefined arguments, which occur if the
    # script does not use the --in-place option.
    arg_defaults = [
        ('inplace', False),
        ('backup', None),
    ]
    args = argparser.parse_args(unparsed_args, namespace)
    args.prog = argparser.prog
    for argname, default in arg_defaults:
        if getattr(args, argname, None) is None:
            setattr(args, argname, default)
    if callable(argcheck_fn):
        argcheck_fn(args)
    return args


def wrap_main(main_fn, argparser, **kwargs):
    """Process arguments and call main with appropriate input and output.

    Process arguments with `argparser`, passing `**kwargs` to
    `get_args`, and then call `vrtargslib.trans_main` with the parsed
    arguments, `main_fn` and the possible values of `in_as_text` and
    `out_as_text` in `kwargs`.
    """
    args = get_args(argparser, **kwargs)
    vrtargslib.trans_main(
        args, main_fn, **dict((key, kwargs.get(key)) for key in
                              ['in_as_text', 'out_as_text']))
    return


class InputProcessor:

    """
    An abstract class for a script processing input and writing output.

    A subclass must define at least the method `main` and should
    re-define the class attribute `DESCRIPTION`. The resulting script
    has the common arguments (as specified in the class attribute
    `OPTIONS`) and it reads input and writes output in `main . In the
    simplest case, the code for running the script can be as follows:

      if __name__ == '__main__':
          InputProcessorSubclass().run()

    This class uses the functions defined above.
    """

    DESCRIPTION = None
    """Description of the script to be shown in the usage message"""
    ARGSPECS = None
    """A list of argument specifications, which are pairs (argnames,
    argdict) where argnames is either a single string or a list of
    strings representing argument names and argdict is a dictionary of
    the keyword arguments to be passed to
    `ArgumentParser.add_argument`."""

    class OPTIONS:
        """Input processor option settings. Subclass this class in a
        subclass of InputProcessor to override the defaults; for
        example:
            class OPTIONS(InputProcessor.OPTIONS):
                common_trans_args = False
        """
        common_trans_args = True
        """The script has the common arguments for transformation scripts"""
        arg_inplace = True
        """The script has the --in-place option"""
        in_as_text = False
        """The input is processed as text instead of binary"""
        out_as_text = False
        """The output is written as text instead of binary"""

    def __init__(self):
        """Initialize the class."""
        self._argparser = None
        """Argument parser"""
        self._args = None
        """Parsed command-line arguments"""
        self._progname = None
        """Program name"""

    def run(self, unparsed_args=None):
        """Process command-line arguments and run the main method."""
        if self._argparser is None:
            self._argparser = get_argparser(
                argspecs=self.ARGSPECS,
                common_trans_args=self.OPTIONS.common_trans_args,
                description=self.DESCRIPTION,
                inplace=self.OPTIONS.arg_inplace
            )
        self._progname = self._argparser.prog
        wrap_main(self.main, self._argparser, unparsed_args=unparsed_args,
                  argcheck_fn=self.check_args,
                  in_as_text=self.OPTIONS.in_as_text,
                  out_as_text=self.OPTIONS.out_as_text)

    def check_args(self, args):
        """Check command-line arguments and assign them to self._args."""
        self._args = args

    def main(self, args, inf, ouf):
        """The actual main method, to be implemented in a subclass.

        args is the parsed command line arguments, inf the input
        stream and ouf the output stream.
        """
        pass

    def print_error(self, *msg):
        """Print message msg to standard error."""
        print_error(*msg, progname=self._progname)

    def error_exit(self, *msg):
        """Print message msg to standard error and exit with code 1."""
        error_exit(*msg, progname=self._progname)
