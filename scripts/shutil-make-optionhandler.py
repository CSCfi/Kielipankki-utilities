#! /usr/bin/env python
# -*- coding: utf-8 -*-


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
                (?:\s+(?P<target>[^\s()!]+) (?P<targetextra>(?:!|\(\)))?)?''',
            re.VERBOSE)

    def process_input_stream(self, stream, filename=None):
        self._add_optspec(['h|help usage()', 'show this help'])
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
        # print optspec_lines[0], repr(optspec)
        for name in optspec['names']:
            self._optspec_map[name.strip('-')] = optspec
        optspec['targetfn'] = (optspec['targetextra'] == '()')
        optspec['defaulttrue'] = (optspec['targetextra'] == '!')
        if not optspec['target'] or optspec['targetfn']:
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
            'cmdline',
            'getopt_opts',
            'defaults',
            'help',
            'opthandler',
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

    def _make_output_cmdline(self):
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

    def _make_output_defaults(self):
        defaults = []
        for optspec in self._optspecs:
            if optspec.get('target') and not optspec.get('targetfn'):
                defaultval = (optspec.get('default')
                              or ('1' if optspec.get('defaulttrue') else ''))
                defaults.append(optspec.get('target') + '=' + defaultval)
        return '\n'.join(defaults)

    def _make_output_help(self):
        usage = []
        for optspec in self._optspecs:
            usage.extend(self._make_opt_help(optspec))
        return '\n'.join(usage)

    def _make_opt_help(self, optspec):
        optlist = ', '.join(optspec['names'])
        optarg = optspec.get('optargname')
        if optarg:
            optlist += ' ' + optarg
        optlist = textwrap.fill(
            optlist, width=self._help_width,
            initial_indent=self._help_indent_text['opt'],
            subsequent_indent=self._help_indent_text['opt'])
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

    def _make_output_opthandler(self):
        code = [
            '''while [ "x$1" != "x" ]; do
    case "$1" in''']
        for optspec in self._optspecs:
            code.extend(self._make_single_opt_handler(optspec))
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

    def _make_single_opt_handler(self, optspec):
        indent8 = ' ' * 8
        indent12 = ' ' * 12
        code = []
        code.append(indent8 + ' | '.join(optspec['names']) + ' )')
        if optspec.get('optargname'):
            code.append(indent12 + 'shift')
        set_line = optspec['target']
        if optspec.get('targetfn'):
            if optspec.get('optargname'):
                set_line += ' $1'
        else:
            set_line += '=' + ('$1' if optspec.get('optargname')
                               else ('' if optspec.get('defaulttrue') else '1'))
        code.append(indent12 + set_line)
        code.append(indent12 + ';;')
        return code


if __name__ == "__main__":
    ShellOptionHandlerGenerator().run()
