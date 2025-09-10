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

from argparse import ArgumentParser
from collections import defaultdict
from enum import Enum, Flag

import vrtargslib

from libvrt.groupargs import ArgumentGrouping


class CommonArgs(Enum):
    """Which arguments common to VRT tools to use"""
    none = 0
    """None (allows code to be reused more easily in other scripts)"""
    version = 1
    """Only --version"""
    trans = 2
    """Common arguments for text transforming scripts"""


class WarningsStyle(Flag):
    """The style of warnings output"""
    NONE = 0
    """No warnings"""
    FIRST = 1
    """Only the first warning of each kind"""
    SUMMARY = 2
    """Summary of warnings (kinds and counts)"""
    ALL = 4
    """All warnings"""


def get_argparser(argspecs=None, *, common_args=CommonArgs.trans,
                  extra_types=None, **kwargs):
    """Return an ArgumentParser with common and possibly other arguments.

    Return an `ArgumentParser` with common arguments by calling
    `vrtargslib.trans_args` (or `vrtargslib.version_args`); see their
    documentation for information on the common arguments.
    Arguments:
      `argspecs`: a list of command-line argument specifications in
          addition to the common ones; see `argparser_add_args` for
          the format
      `common_args`: which common arguments to add (a value in
          CommonArgs)
      `extra_types`:  dict[str, function] of additional types allowed
          in argument specifications in addition to global and
          built-in types
      `**kwargs` is passed to `vrtargslib.trans_args`,
          `vrtargslib.version_args` or `argparse.ArgumentParser`,
          depending on `common_args`, and should contain at least a
          `description` and possibly `inplace=False`, if the
          --in-place argument is not requested.
    """

    if common_args == CommonArgs.trans:
        argparser = vrtargslib.trans_args(**kwargs)
    else:
        if 'inplace' in kwargs:
            del kwargs['inplace']
        if common_args == CommonArgs.version:
            argparser = vrtargslib.version_args(
                description=kwargs.get('description'))
        else:
            argparser = ArgumentParser(**kwargs)
    if argspecs:
        argparser_add_args(argparser, argspecs, extra_types)
    return argparser


def argparser_add_args(argparser, argspecs, extra_types=None):
    """Add the arguments specified in argspecs to ArgumentParser argparser.

    `argspecs` is a list of command-line argument specifications,
    which are in general lists or tuples of 2 or 3 elements:
    (argnames, help, [argdict]), where argnames is either a single
    string or a list or tuple of strings representing argument names
    (and optionally some options, see below), help is the usage string
    and argdict is a dictionary of the keyword arguments to be passed
    to `ArgumentParser.add_argument`.

    Special argnames prefixed with a "#" are used to add a named or
    mutually exclusive argument group or grouped arguments, in which
    case the meaning of content of the second and third element are
    different. See below for more details.

    If argdict (or argnames) contains a default value, information
    about it is appended to the usage string, unless the usage string
    already contains the word "default". Alternatively, argdict may
    contain a value for "silent_default", which is converted to
    "default" but whose value is not appended to the usage string.

    argnames (or its first element) is of the following form:
        argname ('|' | ' ' | ',') argname)* ('=' metavar)? (':' type)?
        ('=' default_or_choices
         | '='? ('(' default_or_choices ')' | '"' default_or_choices '"'))?
        ('/'? nargs)? (('->' | ' ') '!'? dest)?
    where default_or_choices is of the form
        default | ('*'? choice ("|" '*'? choice)+)

    Each argname is an alternative name for the argument, and metavar,
    type, default, nargs and dest correspond to the keyword arguments
    of `ArgumentParser.add_argument` with the same names. Choices can
    be specified in place of the default value; the default choice is
    prefixed with an asterisk. The components may have spaces between
    them. The "=" preceding default and the "->" preceding dest may be
    left out, but the interpretation may change, depending on the
    other components present.

    If no metavar is specified and argdict has none of action,
    choices, default, metavar, nargs or type, add action='store_true',
    or action='store_false' if dest is preceded by an exclamation mark
    (which is allowed only if none of choices, default, metavar, nargs
    or type is present).

    A named argument group is specified with the special argnames
    "#GROUP title" (case-insensitive) where title is the title of the
    group. In this case the second element of the tuple (or list) is the
    description of the group and third is a list of argument
    specifications in the form described above.

    An argument group for grouped command-line arguments is specified
    with the special argnames "#GROUPED title" (case-insensitive),
    which is similar in form to "#GROUP" above but the first argument
    specification specifies the *grouping argument* and the rest the
    *grouped arguments*. The value of the grouping argument is a dict
    mapping from grouping argument values to namespaces containing
    values for the grouped arguments (default: {}). The values of
    grouped arguments are attached to the preceding value of the
    grouping argument, and the values of grouped arguments preceding
    any grouping argument are set as default values in cases where a
    grouped argument is not given a value after a grouping argument.
    (See libvrt.groupargs for more information.)

    A mutually exclusive argument group is specified with the special
    argnames beginning with "#EXCLUSIVE" (case-insensitive), in which
    case the second element of the tuple (or list) is a list of argument
    specifications in the form described above. If "#EXCLUSIVE" is
    followed by "REQUIRED", one of the arguments in the group is
    required.

    Note that many of the argspec components are meaningful only for
    optional arguments, with names beginning with a hyphen. Also note
    that nargs currently supports only ?, * and +, not integer values.
    In general, keyword argument values that cannot be expressed in
    the above format, need to be passed via argdict.

    Argument `extra_types` is dict[str, function] of additional types
    allowed in argument specifications in addition to global and
    built-in types.
    """

    def update_argdict(argspec, key, value):
        """Return `argspec` with its argdict updated with {`key`: `value`}."""
        if len(argspec) == 3:
            argspec[2][key] = value
            return argspec
        else:
            return (argspec[0], argspec[1], {key: value})

    for argspec in argspecs or []:
        optname_u = argspec[0].upper()
        if optname_u.startswith('#EXCLUSIVE'):
            group = argparser.add_mutually_exclusive_group(
                required=('REQUIRED' in optname_u))
            for argspec_sub in argspec[1]:
                _argparser_add_arg(group, argspec_sub, extra_types)
        elif optname_u.startswith('#GROUP'):
            group_title = argspec[0].split(None, 1)[1]
            group_descr = argspec[1]
            group = argparser.add_argument_group(group_title, group_descr)
            if optname_u.startswith('#GROUPED'):
                grouping = ArgumentGrouping()
                _argparser_add_arg(
                    argparser,
                    # The value of the grouping argument defaults to
                    # {}, not shown in the usage
                    update_argdict(argspec[2][0], 'silent_default', {}),
                    extra_types, lambda action: grouping.grouping_arg())
                for argspec_sub in argspec[2][1:]:
                    _argparser_add_arg(
                        group, argspec_sub, extra_types,
                        lambda action: grouping.grouped_arg(action))
            else:
                for argspec_sub in argspec[2]:
                    _argparser_add_arg(group, argspec_sub, extra_types)
        else:
            _argparser_add_arg(argparser, argspec, extra_types)


def _argparser_add_arg(argparser, argspec, extra_types=None,
                       modify_action=None):
    """Add the argument specified in argspec to ArgumentParser argparser.

    See `argparser_add_args` for the format of `argspec`.

    `extra_types` is dict[str, function] of additional types allowed
    in argument specifications in addition to global and built-in
    types.

    If `modify_action` is not `None`, it should be a function of one
    argument, and the `action` of the argument to be added is replaced
    by the value returned by `modify_action(action)`.
    """

    # TODO: Support integer-valued nargs. That may require changes to
    # handling metavar and default, since the value of metavar should
    # then be a tuple and default a list.

    def del_keys(dict_, keys):
        for key in keys:
            if key in dict_:
                del dict_[key]

    def parse_argspec(argspec):
        # Parse argspec and return a dictionary of the components.
        mo = re.match(
            r"""(?P<names> [^=:"\(/>!]+)
                (?: \s* = \s* (?P<metavar> \S+?) )?
                (?: \s* : \s* (?P<type> \S+?) )?
                (?: \s* = \s* (?P<default1> [^\s"\(] \S*?)
                 |  (?: \s* =? \s* (?: " (?P<default2> .*?) "
                                    |  \( (?P<default3> .*?) \) ) ) )?
                (?: \s* (/ \s*)? (?P<nargs> [?*+]) )?
                (?: (?: \s+ | \s* -> \s*) (?P<neg> !)?
                    \s* (?P<dest> (?! \d) \w+?) )?
                $ """,
            argspec, re.VERBOSE)
        if not mo:
            raise vrtargslib.BadCode(
                'Invalid argument specification string: ' + argspec)
        argdict0 = dict((key, val) for key, val in mo.groupdict().items()
                        if val is not None)
        # Do not use ... or ... as the value may be the empty string
        default = argdict0.get('default1',
                               argdict0.get('default2',
                                            argdict0.get('default3')))
        if default is not None:
            argdict0['default'] = default
            del_keys(argdict0, ['default1', 'default2', 'default3'])
        # FIXME: This does not take into account the parameters passed
        # via the explicit argdict.
        if ('neg' in argdict0
            and any(key in argdict0 for key in ['metavar', 'type', 'default',
                                                'nargs'])):
            raise vrtargslib.BadCode(
                'Invalid argument specification string: "!" cannot be used'
                ' with metavar, type, default nor nargs: ' + argspec)
        return argdict0

    def get_type_by_name(typename):
        # Get the type (class) named typename or raise an exception if
        # it is not in built-ins or globals.
        realtype = (globals().get(typename)
                    or globals()['__builtins__'].get(typename)
                    or extra_types.get(typename))
        if realtype is None:
            raise vrtargslib.BadCode(
                'Unsupported type in argument specification string: '
                + typename)
        return realtype

    def process_default_or_choices(argdict0, value_type):
        # Process the possible default or value choices in the
        # argument dictionary.
        if 'default' in argdict0:
            default = argdict0['default']
            if '|' in default and len(default) > 1:
                choices = re.split(r'\s*\|\s*', default.strip())
                default = (list(filter(lambda s: s and s[0] == '*', choices))
                           or None)
                if default:
                    default = default[0][1:]
                    choices = [choice.lstrip('*') for choice in choices]
                if value_type:
                    choices = [value_type(choice) for choice in choices]
                argdict0['choices'] = choices
            if default is not None:
                if value_type:
                    default = value_type(default)
                argdict0['default'] = default
            else:
                del argdict0['default']

    def process_argnames(argnames):
        # If alternative option argument names omit the leading
        # hyphens, add them.
        isoptarg = (argnames[0][0] == '-')
        if isoptarg:
            for i in range(1, len(argnames)):
                if argnames[i][0] != '-':
                    prefix = ('-' if len(argnames[i]) == 1 else '--')
                    argnames[i] = prefix + argnames[i]

    if len(argspec) < 2:
        raise vrtargslib.BadCode(
            'Argument specification needs at least name and help text')
    extra_types = extra_types or {}
    argnames, arghelp = argspec[:2]
    # Convert argnames to a list for futher processing
    if isinstance(argnames, str):
        argnames = [argnames]
    elif isinstance(argnames, tuple):
        argnames = list(argnames)
    argdict = (argspec[2] or {}) if len(argspec) > 2 else {}
    argdict['help'] = arghelp
    # Parse (the first element of) argnames
    argdict0 = parse_argspec(argnames[0])
    # print(repr(argdict0))
    if 'type' in argdict0:
        argdict0['type'] = get_type_by_name(argdict0['type'])
    process_default_or_choices(
        argdict0, argdict.get('type', argdict0.get('type')))
    # Split argument name by spaces, vertical bars and commas
    argnames[0:1] = re.split(r'\s*[\s|,]\s*', argdict0['names'].strip())
    # Values from the explicit dictionary override those from the
    # argspec
    argdict0.update(argdict)
    argdict = argdict0
    if (not any(key in argdict for key in ['action', 'choices', 'default',
                                           'metavar', 'nargs', 'type'])
        and argnames[0][0] == '-'):
        argdict['action'] = 'store_false' if 'neg' in argdict else 'store_true'
    if modify_action:
        argdict['action'] = modify_action(argdict.get('action'))
    del_keys(argdict, ['names', 'neg'])
    process_argnames(argnames)
    # Add information on the possible default value to the usage
    # message, unless it already contains the string "default".
    if 'default' in argdict and 'default' not in argdict['help']:
        default_val = argdict['default']
        # If the default value is bytes, format it directly as a
        # string to get "..." instead of b'...'
        if isinstance(default_val, bytes):
            default_fmt = f'"{default_val.decode("UTF-8")}"'
        else:
            default_fmt = (
                '%(default)s' if 'type' in argdict else '"%(default)s"')
        argdict['help'] += ' (default: ' + default_fmt + ')'
    # silent_default is a default not to be mentioned in the help text
    if 'silent_default' in argdict:
        if 'default' not in argdict:
            argdict['default'] = argdict['silent_default']
        del argdict['silent_default']
    # print(repr(argnames), repr(argdict))
    argparser.add_argument(*argnames, **argdict)


def error_exit(*msg, exitcode=1, **kwargs):
    """Print message msg to standard error and exit with code exitcode.

    kwargs may contain progname, filename and/or linenr: if not None,
    prepend them to the error message.
    """
    print_error(*msg, **kwargs)
    exit(exitcode)


def print_error(*msg, progname=None, filename=None, linenr=None):
    """Print message msg to standard error.

    If progname, filename and/or linenr is not None, prepend them to
    the error message.
    """
    if filename is not None:
        if linenr is not None:
            filename += ':' + str(linenr)
        msg = (filename + ':',) + msg
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
        ('sibling', None),
        ('infile', None),
        ('outfile', None),
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


class BasicProcessor:

    """
    An abstract class for a script taking arguments.

    A concrete subclass should re-define the class attribute
    `DESCRIPTION`.

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
    EPILOG = None
    """Usage epilog shown after argument descriptions"""

    class OPTIONS:
        """Input processor option settings. Subclass this class in a
        subclass of BasicProcessor to override the defaults; for
        example:
            class OPTIONS(BasicProcessor.OPTIONS):
                common_args = CommonArgs.trans
        """
        common_args = CommonArgs.version
        """The script has the common arguments for transformation scripts"""

    def __init__(self, extra_types=None):
        """Initialize the class.

        `extra_types` is a dict[str, function] of additional types
        allowed in argument specifications in addition to global and
        built-in types.
        """
        # Call super to allow use in multiple inheritance
        super().__init__()
        self._argparser = None
        """Argument parser"""
        self._args = None
        """Parsed command-line arguments"""
        self._progname = None
        """Program name"""
        self._extra_types = extra_types
        """Dictionary of extra type functions for argument specifications"""
        self._warnings_style = WarningsStyle.ALL
        """Warnings style"""
        self._warning_counts = defaultdict(int)
        """Number of each kind of warning (for WarningsStyle.SUMMARY)"""
        self._warning_firsts = {}
        """(filename, linenr) for the first of each kind of warning"""

    def _get_argparser(self, **extra_kwargs):
        """Create a parser for command-line arguments."""
        if self._argparser is None:
            self._argparser = get_argparser(
                argspecs=self.ARGSPECS,
                common_args=self.OPTIONS.common_args,
                description=self.DESCRIPTION,
                epilog=self.EPILOG,
                extra_types=self._extra_types,
                **extra_kwargs
            )
        self._progname = self._argparser.prog

    def check_args(self, args):
        """Check command-line arguments and assign them to self._args."""
        self._args = args

    def set_warnings_style(self, style):
        """Set warnings style to `style`."""
        self._warnings_style = style

    def print_error(self, *msg, **kwargs):
        """Print message msg to standard error.

        Prepend program name and possible filename and linenr from kwargs.
        """
        print_error(*msg, progname=self._progname, **kwargs)

    def warn(self, *msg, **kwargs):
        """Print message `msg` prepended with "Warning:" to standard error.

        Prepend program name and possible `filename` and `linenr` from
        `kwargs`.

        Obey `self._warnings_style` (see `WarningsStyle` above).
        `kwargs[kind]` can be used to specify the kind of warning for
        summarization, to be used instead of `msg`. If
        `kwargs[omit_summary]` is specified and truthy, omit the
        warning from the summary.
        """
        if self._warnings_style == WarningsStyle.NONE:
            return
        kind = kwargs.pop('kind', None) or ' '.join(msg)
        omit_summary = kwargs.pop('omit_summary', False)
        if (self._warnings_style & WarningsStyle.ALL
              or (self._warnings_style & WarningsStyle.FIRST
                  and self._warning_firsts.get(kind) is None)):
            self.print_error('Warning:', *msg, **kwargs)
        if self._warnings_style & (WarningsStyle.FIRST | WarningsStyle.SUMMARY):
            self._warning_firsts.setdefault(
                kind, (kwargs.get('filename'), kwargs.get('linenr')))
        if not omit_summary and self._warnings_style & WarningsStyle.SUMMARY:
            self._warning_counts[kind] += 1

    def summarize_warnings(
            self, heading='Summary of warnings ({format}):',
            format='{count}{first_loc}: {kind}',
            first_loc_format=' ({filename}:{linenr})',
            heading_placeholders=None,
            prepend_progname=True):
        """Print a summary of warnings to standard error.

        Preprend a line with `heading` (`None` or empty to suppress)
        and format each summary line according to `format` and
        `first_loc_format`. If `include_progname` is `True` (default),
        prepend program name to each summary line; `False` to
        suppress. `heading` may contain `{format}`, which is replaced
        with the format of a summary line, with format fields replaced
        by placeholders. The default placeholders can be overridden
        with `heading_placeholders` (`dict`).
        """
        if not self._warning_counts:
            return
        print_func = self.print_error if prepend_progname else print_error
        if heading:
            heading_placeholders = heading_placeholders or dict(
                count='<count>',
                kind='<kind>',
                filename='<file name of first>',
                linenr='<line number>'
            )
            print_func(heading.replace('{format}', format)
                       .replace('{first_loc}', first_loc_format)
                       .format(**heading_placeholders))
        for kind, count in self._warning_counts.items():
            filename, linenr = self._warning_firsts[kind]
            first_loc = ('' if filename is None
                         else first_loc_format.format(filename=filename,
                                                      linenr=linenr))
            s = 's' if count > 1 else ''
            print_func(format.format(count=count, first_loc=first_loc,
                                     filename=filename, linenr=linenr,
                                     s=s, kind=kind))

    def error_exit(self, *msg, exitcode=1, **kwargs):
        """Print message msg to standard error and exit with code exitcode.

        Prepend program name and possible filename and linenr from kwargs.
        """
        error_exit(*msg, exitcode=exitcode, progname=self._progname, **kwargs)


class InputProcessor(BasicProcessor):

    """
    An abstract class for a script processing input and writing output.

    A subclass must define at least the method `main` and should
    re-define the class attribute `DESCRIPTION`. The resulting script
    has the common arguments (as specified in the class attribute
    `OPTIONS`) and it reads input and writes output in `main . In the
    simplest case, the code for running the script can be as follows:

      if __name__ == '__main__':
          InputProcessorSubclass().run()
    """

    class OPTIONS(BasicProcessor.OPTIONS):
        """Input processor option settings. Subclass this class in a
        subclass of InputProcessor to override the defaults; for
        example:
            class OPTIONS(InputProcessor.OPTIONS):
                arg_inplace = False
        """
        common_args = CommonArgs.trans
        """The script has the common arguments for transformation scripts"""
        arg_inplace = True
        """The script has the --in-place option"""
        in_as_text = False
        """The input is processed as text instead of binary"""
        out_as_text = False
        """The output is written as text instead of binary"""

    def __init__(self, **kwargs):
        """Initialize the class."""
        super().__init__(**kwargs)

    def run(self, unparsed_args=None):
        """Process command-line arguments and run the main method."""
        self._get_argparser(inplace=self.OPTIONS.arg_inplace)
        wrap_main(self.main, self._argparser, unparsed_args=unparsed_args,
                  argcheck_fn=self.check_args,
                  in_as_text=self.OPTIONS.in_as_text,
                  out_as_text=self.OPTIONS.out_as_text)

    def main(self, args, inf, ouf):
        """The actual main method, to be implemented in a subclass.

        args is the parsed command line arguments, inf the input
        stream and ouf the output stream.
        """
        pass
