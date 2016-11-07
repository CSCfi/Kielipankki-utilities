#! /usr/bin/env python
# -*- coding: utf-8 -*-


# TODO:
# - Handle options that can be specified many times: either multiple
#   calls to a function or a single value with a specified separator
# - Group options in the usage message
# - Continuation lines in option specifications


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

optname1|...|optnamen[=ARG] ["default"] [([!]target | {code})]
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
  to shell variables are (typically) expanded in the shell script.
- target: The shell variable corresponding to the option value. If
  not specified, the variable is the first long option name with
  dashes converted to underscores. If the target is immediately
  preceded by !, the default value (for an argumentless option) is 1
  and the option resets it to the empty string.
- {code}: Shell script code (for example, a function call) to be
  executed when encountering the option, instead of directly setting a
  variable value. In the code, the option argument value can be
  referred to as $1 and the option itself as $optname.
- description: A description of the option for the usage message; may
  span several lines, each beginning with whitespace; is subject to
  reformatting (word wrapping).

Empty lines and lines beginning with a # are ignored.

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

The script generates the following sections:

- cmdline_args: target script options and arguments (appropriately
  quoted for 'eval set -- "$args"'), taking into account values from a
  configuration file;
- getopt_opts: getopt option specifications (arguments for -o and -l)
  as shell variable assignments (for 'eval "..."');
- set_defaults: setting defaul values as shell variable assignments
  (for 'eval "..."');
- opt_usage: option descriptions for a usage message; and
- opt_handler: the actual option handler (a case statement, for 'eval
  "..."').
"""


import re
import codecs
import textwrap
# configparser in Python 3
import ConfigParser as configparser

from collections import defaultdict
from optparse import OptionParser

import korpimport.util


class ShellOptionHandlerGenerator(korpimport.util.BasicInputProcessor):

    def __init__(self, args=None):
        super(ShellOptionHandlerGenerator, self).__init__()
        self._optspecs = []
        self._optspec_map = {}
        self._opts = None
        self._args = None
        self._help_indent = {'opt': 2, 'text': 18}
        self._help_indent_text = dict(
            (key, val * ' ') for key, val in self._help_indent.iteritems())
        self._help_width = 78
        # FIXME: Handle defaults containing double quotes
        self._optspec_re = re.compile(
            r'''(?P<optnames>[^\s=:]+)
                (?:[=:](?P<optargname>\S+))?
                (?:\s+(?P<default>"[^\"]*"))?
                (?:\s+(?:
                    (?P<targetneg> ! \s*)? (?P<target> [a-zA-Z0-9_]+)
                  | \{\s* (?P<targetcode> .*) \s*\}
                ))?''',
            re.VERBOSE)

    def process_input_stream(self, stream, filename=None):
        self._add_optspec(['h|help {usage}', 'show this help'])
        self._read_optspecs(stream)
        # print repr(self._optspecs)
        self._parse_opts()
        # print repr(self._optspecs)
        if self._opts._config_file:
            self._read_config_file()
        # print repr(self._optspecs)
        self._write_output()

    def _read_optspecs(self, stream):
        optspec_lines = []
        for line in stream:
            line_strip = line.strip()
            if not line_strip or line_strip[0] == '#':
                continue
            if line[0] not in [' ', '\t']:
                self._add_optspec(optspec_lines)
                optspec_lines = []
            optspec_lines.append(line_strip)
        self._add_optspec(optspec_lines)

    def _add_optspec(self, optspec_lines):
        if not optspec_lines:
            return
        optspec = {}
        mo = self._optspec_re.match(optspec_lines[0])
        if not mo:
            self.error('Invalid option specification line: ' + optspec_lines[0])
        optspec.update(mo.groupdict())
        optspec['names'] = [('-' + name if len(name) == 1 else '--' + name)
                            for name in optspec['optnames'].split('|')]
        # print repr(optspec_lines[0]), repr(optspec)
        for name in optspec['names']:
            self._optspec_map[name.strip('-')] = optspec
        optspec['defaulttrue'] = (optspec['targetneg'] == '!')
        if not optspec['target'] or optspec['targetcode']:
            long_opts = [name for name in optspec['names'] if len(name) > 2]
            target_name = long_opts[0] if long_opts else optspec['names'][0]
            optspec['pytarget'] = target_name.strip('-').replace('-', '_')
            if not optspec['target']:
                optspec['target'] = optspec['pytarget']
        else:
            optspec['pytarget'] = optspec['target']
        optspec['descr'] = (
            ' '.join(optspec_lines[1:]) if len(optspec_lines) > 1 else '')
        self._optspecs.append(optspec)

    def _parse_opts(self):
        optparser = OptionParser(usage='', add_help_option=False)
        for optnames, optopts in [
                [['config-file'], dict()],
                [['config-file-option-name'], dict()],
                [['config-section'], dict(default='Default')],
                [['output-section-format'],
                 dict(default=u'----- {name}\n{content}\n-----\n')],
        ]:
            optparser.add_option(*['--_' + name for name in optnames],
                                 **optopts)
        for optspec in self._optspecs:
            optopts = {'dest': optspec['pytarget']}
            if optspec['optargname'] is None:
                optopts['action'] = 'store_true'
            optparser.add_option(*optspec['names'], **optopts)
        self._opts, self._args = optparser.parse_args()
        config_file_opt = self._opts._config_file_option_name
        if config_file_opt:
            optval = getattr(self._opts,
                             config_file_opt.lstrip('-').replace('-', '_'),
                             None)
            if optval:
                self._opts._config_file = optval
        self._opts._output_section_format = unicode(
            self._opts._output_section_format.replace('\\n', '\n'))
        for optspec in self._optspecs:
            optspec['value'] = getattr(self._opts, optspec['pytarget'], None)

    class ConfigReader(object):

        """Add a [Default] section at the beginning of the config file."""

        def __init__(self, fname, encoding='utf-8'):
            self._first = True
            self._file = codecs.open(fname, 'r', encoding=encoding)

        def readline(self):
            if self._first:
                self._first = False
                return '[Default]\n'
            else:
                return self._file.readline()

        def close(self):
            self._file.close()

    def _read_config_file(self):
        reader = self.ConfigReader(self._opts._config_file,
                                   self._input_encoding)
        try:
            confparser = configparser.SafeConfigParser()
            confparser.optionxform = str
            confparser.readfp(reader, self._opts._config_file)
            reader.close()
            config_items = confparser.items(self._opts._config_section)
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
                optspec['value'] = val

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
                content=(getattr(self, '_make_output_' + sectname)()
                         .decode(self._input_encoding or 'utf-8'))))

    def _shell_quote(self, text, type_='double'):
        quote1 = '"' if type_ == 'double' else '\''
        quote2 = '\'' if type_ == 'double' else '"'
        replquote = quote1 + quote2 + quote1 + quote2 + quote1
        return quote1 + text.replace(quote1, replquote) + quote1

    def _make_output_cmdline_args(self):
        opts = []
        for optspec in self._optspecs:
            if optspec['value'] is not None:
                opts.append(optspec['names'][0])
                if optspec.get('optargname'):
                    opts.append(self._shell_quote(optspec['value']))
        return ' '.join(opts + [self._shell_quote(arg) for arg in self._args])

    def _make_output_getopt_opts(self):
        shortopts = []
        longopts = []
        for optspec in self._optspecs:
            argmarker = ':' if optspec.get('optargname') else ''
            shortopts.extend(name.strip('-') + argmarker
                             for name in optspec['names'] if len(name) == 2)
            longopts.extend(name.strip('-') + argmarker
                            for name in optspec['names'] if len(name) > 2)
        return ('shortopts="' + ''.join(shortopts) + '"\n'
                'longopts="' + ','.join(longopts) + '"')

    def _make_output_set_defaults(self):
        defaults = []
        for optspec in self._optspecs:
            if optspec.get('target') and not optspec.get('targetcode'):
                defaultval = (optspec.get('default')
                              or ('1' if optspec.get('defaulttrue') else ''))
                defaults.append(optspec.get('target') + '=' + defaultval)
        return '\n'.join(defaults)

    def _make_output_opt_usage(self):
        usage = []
        for optspec in self._optspecs:
            usage.extend(self._make_opt_usage_single(optspec))
        return '\n'.join(usage)

    def _make_opt_usage_single(self, optspec):
        optlist = ', '.join(optspec['names'])
        optarg = optspec.get('optargname')
        if optarg:
            optlist += ' ' + optarg
        optlist = textwrap.fill(
            optlist, width=self._help_width,
            initial_indent=self._help_indent_text['opt'],
            subsequent_indent=self._help_indent_text['opt'],
            break_on_hyphens=False)
        helptext = optspec.get('descr') or ''
        default = optspec.get('default')
        if default:
            helptext += (' ' if helptext else '') + '(default: ' + default + ')'
        if helptext:
            helptext = textwrap.fill(
                helptext, width=self._help_width,
                initial_indent=self._help_indent_text['text'],
                subsequent_indent=self._help_indent_text['text'])
        if len(optlist) <= self._help_indent['text'] - 2:
            return [optlist + helptext[len(optlist):]]
        elif helptext:
            return [optlist, helptext]
        else:
            return [optlist]

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
