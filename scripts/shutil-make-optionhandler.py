#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# TODO:
# - Specify value separator for options that can be specified many
#   times (syntax maybe *"sep", *(sep) or *[sep]).
# - Support specifying a hard line break in the option description.
# - Optionally strip quotes from values specified in a configuration
#   file. The quote type should determine the quote type for the
#   command-line arguments, overriding other specifications. The
#   stripping option could be enabled by a ^ in the option
#   specification after the quote type.
# - Obligatory options: error message if missing. Would it be better
#   to output the error from the Python code or generate shell script
#   code for checking if the option is specified?
# - Pass-through options: allow unrecognized options to be collected,
#   probably to a separate output section, so that this script can be
#   used to handle options in wrapper scripts that process only some
#   of the options while passing the rest to a called script. That
#   requires either converting to use argparse (parse_known_args) or
#   subclassing OptionParser (https://stackoverflow.com/a/9307174).
# - Options without a value in the configuration file. This would be
#   simple with ConfigParser for Python 2.7 (allow_no_value=True), but
#   how about with Python 2.6?
# - A marker in the option specification to allow non-option arguments
#   interspersed with options. This cannot be a script option, since
#   interspersed arguments would need to be enabled before parsing
#   script arguments.
# - More generally, a method of passing script options via the option
#   specification input. That would make sense in particular for
#   specifying the option name for configuration file.


"""
shutil-make-optionhandler.py

Usage: shutil-make-optionhandler.py [options] [script_options]
           [script_arguments] < option_specifications

Generate option processing code for Bourne-like shell scripts (should
also work in other shells than Bash) based on option specifications
read from the standard input. script_options and script_arguments are
passed to the target (calling) script, the options possibly modified
by values read from a configuration file (INI-syntax).

An option specification is of the form

optname1|...|optnamen[=ARG] ["default"] ['|"] [*] [[!]target] [{code}]
  description
  ...

The first line may not have leading whitespace, whereas the
description lines must have. The components are as follows:

- optnameN: Option names, separated by vertical bars. Single-letter
  option names correspond to short options, others to long ones.
- =ARG: If specified, the option takes an argument. ARG is used in the
  usage message for the option.
- "default": The default (initial) value for the variable
  corresponding to the option, enclosed in double quotes. References
  to shell variables are (typically) expanded in the shell script. A
  double quote (or a backslash) in the value itself must be escaped by
  a backslash.
- '|": The option values read from a configuration file should be
  enclosed in this kind of quotes in the generated command-line
  arguments instead of the default ones (double quotes unless
  --_config-values-single-quoted is specified).
- *: The option may be specified multiple times. If option handler
  code is specified ({code}), it will be called separately for each
  value. Otherwise, the target value will contain all the argument
  values separated by a newline. The asterisk must be preceded and may
  be followed by whitespace.
- target: The shell variable corresponding to the option value. If
  not specified, the variable is the first long option name with
  dashes converted to underscores. If the target is immediately
  preceded by !, the default value (for an argumentless option) is 1
  and the option resets it to the empty string.
- {code}: Shell script code (for example, a function call) to be
  executed when encountering the option, instead of directly setting a
  variable value. In the code, the option argument value can be
  referred to as $1 and the option itself as $optname. A target may
  be specified in addition to code; in that case, the target variable
  is used for setting the default value. (Note that the specified code
  is *not* executed at the initialization phase.) If no target nor
  default value is specified, no variable is initialized.
- description: A description of the option for the usage message; may
  span several lines, each beginning with whitespace; is subject to
  reformatting (word wrapping). If the option has a default value, the
  string "%(default)s" is replaced with it; if not present and if the
  description does not contain the string "(default: " or "(Default:
  ", then "(default: DEFAULT)" is appended to the description (where
  DEFAULT is the default value).

Empty lines and lines beginning with a # are ignored. A line may be
continued on the next line by ending in a backslash. This is useful in
particular for the first line. A continuation line may but need not
have leading whitespace, regardless of whether it continues the first
line or a description line. Any whitespace surrounding the
continuation backslash is replaced with a single space.

Options can be grouped with with lines of the form

@ label

where label is the label for the group to be shown above the options
following in the usage message.

Options to this script are distinguished from the target script
options by having their names prefixed with an underscore. The
currently recognized options are:

--_output-section-format=FORMAT: Format each output section according
  to the format string FORMAT, which may contain the keys {name} for
  section name and {content} for section content. Literal \n is
  replaced with a newline. Default: "----- {name}\n{content}\n-----\n"
--_config-file=FILE: Read FILE as a configuration file
--_config-file-option-name=OPTION: Use the argument of the (target
  script) option OPTION as the name of the configuration file to read
--_config-section=SECT: Read options from configuration file section
  SECT; default: "Default", which may be at the beginning of the
  config file without an explicit section heading.
--_config-values-single-quoted: Generate single-quoted strings from
  option values specified in the configuration file, without expanding
  shell (environment) variables or backquotes. (Single quotes are
  allowed.) By default, the script generates double-quoted strings,
  subject to shell variable and backquote expansion, so literal $, `
  and \ must be protected by a backslash.
--_option-group-label-format=FORMAT: Format each option group label
  according to the format string FORMAT, which must contain the key
  {label} for the group label. Literal \n is replaced with a newline.
  Default: "\n{label}:"

Note that option values specified on the command line are treated as
single-quoted strings when they are processed by this script; the
possible expansions have already been performed by the shell.

The syntax of configuration files have two extensions to that natively
supported by Python's ConfigParser module:

- Options may be specified at the beginning of the configuration file
  without a section heading.

- An option may be specified multiple times in the configuration file
  with different values, corresponding to a command-line option that
  can be specified multiple times. For a single-value option, the last
  specified value takes effect, as usual with ConfigParser.

The script generates the following sections:

- cmdline_args: target script options and arguments (appropriately
  quoted for 'eval set -- "$args"'), taking into account values from a
  configuration file;
- getopt_opts: getopt option specifications (arguments for -o and -l)
  as shell variable assignments (for 'eval "..."');
- set_defaults: setting default values as shell variable assignments
  (for 'eval "..."');
- opt_usage: option descriptions for a usage message; and
- opt_handler: the actual option handler (a case statement, for 'eval
  "..."').
"""


import re
import codecs
import textwrap
# configparser in Python 3
import configparser as configparser

from collections import defaultdict
from optparse import OptionParser

import korpimport3.util

# A similar approach is used in ConfigParser
try:
    from collections import OrderedDict as ConfigBaseDict
except ImportError:
    # For Python 2.6
    ConfigBaseDict = dict


class ShellOptionHandlerGenerator(korpimport3.util.BasicInputProcessor):

    def __init__(self, args=None):
        super(ShellOptionHandlerGenerator, self).__init__()
        self._optspecs = []
        self._optspec_map = {}
        self._opts = None
        self._args = None
        self._help_indent = {'opt': 2, 'text': 18, 'grouplabel': 0}
        self._help_indent_text = dict(
            (key, val * ' ') for key, val in self._help_indent.items())
        self._help_width = 78
        self._optspec_re = re.compile(
            r'''(?P<optnames> [^\s=:]+)
                (?: [=:] (?P<optargname> \S+) )?
                (?: \s+ (?P<default> "([^\"\\]|\\.)*") )?
                (?: \s+
                  (?: (?P<quotetype> [\'\"]) \s* )?
                  (?: (?P<targetmulti> \*) \s* )?
                  (?: (?P<targetneg> ! \s*)? (?P<target> [a-zA-Z0-9_]+) \s* )?
                  (?: \{ \s* (?P<targetcode> .*) \s* \} )?
                )?''',
            re.VERBOSE)
        self._curr_optgroup = None
        self._optgroups = []

    def process_input_stream(self, stream, filename=None):
        self._read_optspecs(stream)
        if 'help' not in self._optspec_map:
            self._add_help_opt()
        # print repr(self._optspecs)
        self._parse_opts()
        # print repr(self._optspecs)
        if self._opts._config_file:
            self._read_config_file()
        # print repr(self._optspecs)
        self._write_output()

    def _read_optspecs(self, stream):
        optspec_lines = []
        continued_line = []
        for line in stream:
            line_strip = line.strip()
            if not line_strip or line_strip[0] == '#':
                continue
            if line[0] not in [' ', '\t'] and not continued_line:
                self._add_optspec(optspec_lines)
                optspec_lines = []
            # FIXME: This does not allow a literal backslash at the
            # end of a line. Should we use a double backslash for
            # that?
            if line_strip[-1] == '\\':
                continued_line.append(line_strip[:-1].strip())
            else:
                optspec_lines.append(' '.join(continued_line + [line_strip]))
                continued_line = []
        if continued_line:
            optspec_lines.append(' '.join(continued_line))
        self._add_optspec(optspec_lines)
        if not self._optgroups:
            self._add_optgroup([])

    def _add_optspec(self, optspec_lines, optgroup=None, prepend=False):
        if not optspec_lines:
            return
        if optspec_lines[0][0] == '@':
            self._add_optgroup(optspec_lines)
            return
        elif not self._optgroups:
            self._add_optgroup([])
        optspec = {}
        mo = self._optspec_re.match(optspec_lines[0])
        if not mo:
            self.error('Invalid option specification line: ' + optspec_lines[0])
        optspec.update(mo.groupdict())
        optspec['names'] = [('-' + name if len(name) == 1 else '--' + name)
                            for name in optspec['optnames'].split('|')]
        # print repr(optspec_lines[0]), repr(optspec)
        for name in optspec['names']:
            try:
                _ = name.encode('ascii')
            except UnicodeEncodeError as e:
                self.error('Invalid non-ASCII option name: ' + name)
        for name in optspec['names']:
            self._optspec_map[name.strip('-')] = optspec
        optspec['defaulttrue'] = (optspec['targetneg'] == '!')
        if not optspec['target']:
            long_opts = [name for name in optspec['names'] if len(name) > 2]
            target_name = long_opts[0] if long_opts else optspec['names'][0]
            optspec['pytarget'] = target_name.strip('-').replace('-', '_')
            optspec['target'] = optspec['pytarget']
        else:
            optspec['pytarget'] = optspec['target']
            optspec['explicit_target'] = True
        optspec['descr'] = (
            ' '.join(optspec_lines[1:]) if len(optspec_lines) > 1 else '')
        self._optspecs.append(optspec)
        if optgroup is None:
            optgroup = self._curr_optgroup
        if prepend:
            optgroup[0:0] = [optspec]
        else:
            optgroup.append(optspec)

    def _add_optgroup(self, optspec_lines):
        if not optspec_lines:
            self._optgroups.append(('', []))
        else:
            self._optgroups.append((optspec_lines[0].strip('@').strip(), []))
        self._curr_optgroup = self._optgroups[-1][1]

    def _add_help_opt(self):
        if self._optgroups[0][0] != '':
            self._optgroups[0:0] = [('Help', [])]
        self._add_optspec(['h|help {usage}', 'show this help'],
                          self._optgroups[0][1], prepend=True)

    def _parse_opts(self):
        optparser = OptionParser(usage='', add_help_option=False)
        optparser.disable_interspersed_args()
        script_opts = [
            [['config-file'], dict()],
            [['config-file-option-name'], dict()],
            [['config-section'], dict(default='Default')],
            [['config-values-single-quoted'], dict(action='store_true')],
            [['output-section-format'],
             dict(default='----- {name}\n{content}\n-----\n')],
            [['option-group-label-format'], dict(default='\n{label}:')],
        ]
        for optnames, optopts in script_opts:
            optparser.add_option(*['--_' + name for name in optnames],
                                 **optopts)
        for optspec in self._optspecs:
            optopts = {'dest': optspec['pytarget']}
            if optspec['optargname'] is None:
                optopts['action'] = 'store_true'
            elif optspec['targetmulti'] is not None:
                optopts['action'] = 'append'
            # print repr(optspec['names']), repr(optopts)
            optparser.add_option(*optspec['names'], **optopts)
        try:
            self._opts, self._args = optparser.parse_args()
        except UnicodeDecodeError as e:
            self.error('Probably a non-ASCII character in an option name on'
                       ' the command-line: ' + str(e))
        config_file_opt = self._opts._config_file_option_name
        if config_file_opt:
            optval = getattr(self._opts,
                             config_file_opt.lstrip('-').replace('-', '_'),
                             None)
            if optval:
                self._opts._config_file = optval
        self._opts._output_section_format = str(
            self._opts._output_section_format.replace('\\n', '\n'))
        self._opts._option_group_label_format = str(
            self._opts._option_group_label_format.replace('\\n', '\n'))
        for optspec in self._optspecs:
            optspec['value'] = getattr(self._opts, optspec['pytarget'], None)

    class ConfigReader(object):

        """Add a [Default] section at the beginning of the config file."""

        def __init__(self, fname, encoding='utf-8-sig'):
            self._first = True
            # Handle possible BOM at the beginning (in a file from Windows)
            if encoding == 'utf-8':
                encoding = 'utf-8-sig'
            self._file = codecs.open(fname, 'r', encoding=encoding)

        def readline(self):
            if self._first:
                self._first = False
                return '[Default]\n'.decode(self._file.encoding)
            else:
                return self._file.readline()

        def close(self):
            self._file.close()

    class ListExtendDict(ConfigBaseDict):

        """Extend old value with new with a '' between if both are lists.

        When setting a value of a key in a dictionary, if a previous
        value exists and if both the previous and the new value are
        lists, instead of replacing the old value with the new one,
        extend the existing list with the new one, with an empty
        string element in between. If a previous value exists and if
        both the previous and the new value are strings, append two
        newlines and the new value to the old value.

        This is used to make ConfigParser handle options that may be
        specified multiple times in the configuration file. They will
        have two consecutive newlines between the different values for
        an option, whereas a single multi-line value has a single
        newline between each line.

        NOTE: This works because (Raw)ConfigParser.read() in Python
        2.7 internally collects multi-line values to lists, and Python
        2.6 collects them to strings. If that changes, this probably
        will not work.
        """

        def __setitem__(self, key, val):
            # print key, repr(val), repr(self)
            if key in self:
                if isinstance(self[key], list) and isinstance(val, list):
                    # Python 2.7
                    self[key].append('')
                    self[key].extend(val)
                    return
                elif (isinstance(self[key], str)
                      and isinstance(val, str)):
                    # Python 2.6
                    val = self[key] + '\n\n' + val
            super(ShellOptionHandlerGenerator.ListExtendDict,
                  self).__setitem__(key, val)

    def _read_config_file(self):
        reader = self.ConfigReader(self._opts._config_file,
                                   self._input_encoding)
        try:
            confparser = configparser.SafeConfigParser(
                dict_type=self.ListExtendDict)
            confparser.optionxform = str
            confparser.readfp(reader, self._opts._config_file)
            reader.close()
            # raw=True: Do not expand %(...) variable references in
            # option values
            config_items = confparser.items(self._opts._config_section,
                                            raw=True)
        except configparser.Error as e:
            self.error('Parsing configuration file: ' + str(e),
                       filename=self._opts._config_file)
        self._set_config_options(config_items)

    def _set_config_options(self, config_items):

        def camel2dash(mo):
            return '-' + mo.group(1).lower()

        for name, val in config_items:
            optname = (name[0].lower() + name[1:]).replace('_', '-')
            optname = re.sub(r'(?<=[a-z])([A-Z])(?=[a-z])', camel2dash,
                             optname)
            # print name, val, optname
            optspec = self._optspec_map.get(optname)
            if optspec is None:
                self.warn('Unrecognized configuration option: ' + name)
            elif optspec.get('value') is None:
                vals = val.split('\n\n')
                if optspec['targetmulti'] is not None:
                    optspec['value'] = vals
                else:
                    # Take the last value
                    optspec['value'] = vals[-1]
                optspec['valuefromconfig'] = True

    def _write_output(self):
        sectnames = [
            'cmdline_args',
            'getopt_opts',
            'set_defaults',
            'opt_usage',
            'opt_handler',
        ]
        # FIXME: Decode here to Unicode, since
        # BasicInputProcessor.output() expects that; however, it again
        # encodes to UTF-8.
        for sectname in sectnames:
            self.output(self._opts._output_section_format.format(
                name=sectname,
                content=(getattr(self, '_make_output_' + sectname)())))

    def _shell_quote(self, text, type_='double'):
        quote1 = '"' if type_ == 'double' else '\''
        quote2 = '\'' if type_ == 'double' else '"'
        replquote = quote1 + quote2 + quote1 + quote2 + quote1
        return quote1 + text.replace(quote1, replquote) + quote1

    def _make_output_cmdline_args(self):
        opts = []
        for optspec in self._optspecs:
            optval = optspec['value']
            if optval is not None:
                if optspec.get('targetmulti'):
                    if optspec.get('targetcode'):
                        for value in optval:
                            opts.extend(self._make_cmdline_opt(optspec, value))
                    else:
                        opts.extend(
                            self._make_cmdline_opt(optspec, '\n'.join(optval)))
                else:
                    opts.extend(self._make_cmdline_opt(optspec, optval))
        return ' '.join(opts + [self._shell_quote(arg) for arg in self._args])

    def _make_cmdline_opt(self, optspec, optval):
        opts = []
        opts.append(optspec['names'][0])
        if optspec.get('optargname'):
            quote_type = (
                'double' if (optspec.get('valuefromconfig')
                             and ((not self._opts._config_values_single_quoted
                                   and optspec['quotetype'] != '\'')
                                  or (self._opts._config_values_single_quoted
                                      and optspec['quotetype'] == '"')))
                else 'single')
            opts.append(self._shell_quote(optval, quote_type))
        return opts

    def _make_output_getopt_opts(self):
        shortopts = []
        longopts = []
        for optspec in self._optspecs:
            argmarker = ':' if optspec.get('optargname') else ''
            shortopts.extend(name.strip('-') + argmarker
                             for name in optspec['names'] if len(name) == 2)
            longopts.extend(name.strip('-') + argmarker
                            for name in optspec['names'] if len(name) > 2)
        # Prepending a + to the short option string makes GNU getopt
        # stop parsing options as soon as it encounters the first
        # non-option argument.
        return ('shortopts="+' + ''.join(shortopts) + '"\n'
                'longopts="' + ','.join(longopts) + '"')

    def _make_output_set_defaults(self):
        defaults = []
        for optspec in self._optspecs:
            if (optspec.get('default') or optspec.get('explicit_target')
                or not optspec.get('targetcode')):
                defaultval = (optspec.get('default')
                              or ('1' if optspec.get('defaulttrue') else ''))
                defaults.append(optspec.get('target') + '=' + defaultval)
        return '\n'.join(defaults)

    def _make_output_opt_usage(self):
        usage = []
        for optgroup in self._optgroups:
            label, optspecs = optgroup
            if label != '':
                usage.append(self._opts._option_group_label_format.format(
                    label=self._wrap_usage_text(label, 'grouplabel',
                                                break_on_hyphens=False)))
            for optspec in optspecs:
                usage.extend(self._make_opt_usage_single(optspec))
        return '\n'.join(usage)

    def _make_opt_usage_single(self, optspec):
        optlist = ', '.join(optspec['names'])
        optarg = optspec.get('optargname')
        if optarg:
            optlist += ' ' + optarg
        optlist = self._wrap_usage_text(optlist, 'opt', break_on_hyphens=False)
        helptext = optspec.get('descr') or ''
        default = optspec.get('default')
        if default:
            if '%(default)s' in helptext:
                helptext = helptext.replace('%(default)s', default)
            elif not re.search(r'\([Dd]efault: ', helptext):
                # FIXME: Testing for "(default: " is potentially a bit fragile;
                # would it be better to have some kind of a directive in the
                # description to suppress the default value?
                if helptext and helptext[-1] == '.':
                    helptext = helptext[:-1] + ' (default: ' + default + ').'
                else:
                    helptext += ((' ' if helptext else '')
                                 + '(default: ' + default + ')')
        if helptext:
            helptext = self._wrap_usage_text(helptext, 'text')
        if len(optlist) <= self._help_indent['text'] - 2:
            return [optlist + helptext[len(optlist):]]
        elif helptext:
            return [optlist, helptext]
        else:
            return [optlist]

    def _wrap_usage_text(self, text, text_type, break_on_hyphens=True):
        return textwrap.fill(
            text, width=self._help_width,
            initial_indent=self._help_indent_text[text_type],
            subsequent_indent=self._help_indent_text[text_type],
            break_on_hyphens=break_on_hyphens)

    def _make_output_opt_handler(self):
        code = [
            '''while [ "x$1" != "x" ]; do
    optname=$1
    case "$optname" in''']
        for optspec in self._optspecs:
            code.extend(self._make_opt_handler_single(optspec))
        code.append(
            '''
        -- )
	    shift
	    break
	    ;;
	--* )
	    warn "Unrecognized option: $1"
	    ;;
	* )
	    break
	    ;;
    esac
    shift
done''')
        return '\n'.join(code)

    def _make_opt_handler_single(self, optspec):
        indent8 = ' ' * 8
        indent12 = ' ' * 12
        code = []
        code.append(indent8 + ' | '.join(optspec['names']) + ' )')
        if optspec.get('optargname'):
            code.append(indent12 + 'shift')
        if optspec.get('targetcode'):
            set_line = optspec.get('targetcode')
        else:
            set_line = (
                optspec['target'] + '='
                + ('$1' if optspec.get('optargname')
                   else ('' if optspec.get('defaulttrue') else '1')))
        code.append(indent12 + set_line)
        code.append(indent12 + ';;')
        return code


if __name__ == "__main__":
    ShellOptionHandlerGenerator().run()
