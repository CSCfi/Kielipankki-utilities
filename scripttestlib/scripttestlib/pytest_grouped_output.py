
"""
Pytest plugin for grouped parametrized test output.

This plugin provides a custom reporter that groups the output of parametrized
tests by their parent test function, making it clearer which function's tests
are currently running.

By default, this plugin is specifically designed for scripttestlib-based tests
but can be configured to apply to other test modules.

Grouping is active only at the default verbosity and with -q, as with -v,
pytest shows each test on a line of its own.

Usage:
------
Call the hook functions of this module from the corresponding hooks in
conftest.py, as the shared scripttestlib/tests/conftest.py does:

    def pytest_addoption(parser):
        scripttestlib.pytest_grouped_output.pytest_addoption(parser)

    def pytest_configure(config):
        scripttestlib.pytest_grouped_output.pytest_configure(config)

Alternatively, register this module as a plugin in pytest.ini or in the
top-level conftest.py:
    pytest_plugins = ["scripttestlib.pytest_grouped_output"]
The functions are idempotent, so doing both does no harm.

Configuration via command-line options:
    --scripttest-grouped-modules=PATTERNS
          Glob patterns of test modules to group (default: test_scripts*)
    --scripttest-grouped-output=FORMAT
          Output format: 'short' (default), 'full' or 'none':
          'short': Simplified names (removes prefixes/suffixes)
          'full': Complete function names
          'none': Disable grouping, use standard pytest output

Example output with default settings (short format):
    test_scripts.py::hrt_encode_tags .................................... [ 12%]
    .........................................................................
    test_scripts.py::vrt_drop_attrs ..................................... [ 45%]
    .........................................................................

With --scripttest-grouped-output=full:
    test_scripts.py::test_scripttest_hrt_encode_tags_yaml ............... [ 12%]
    .........................................................................
    test_scripts.py::test_scripttest_vrt_drop_attrs_yaml ................ [ 45%]
    .........................................................................

With --scripttest-grouped-output=none:
    Uses standard pytest output (no grouping headers)

Implementation:
    This plugin uses pytest's public hook API (pytest_runtest_logstart) to
    intercept test runs and insert group headers. The terminal writer is
    obtained via the public get_terminal_writer() method.
"""


import fnmatch
import re
import weakref

import pytest


# pytest option parsers to which the options of this plugin have been
# added by pytest_addoption
_option_parsers = weakref.WeakSet()


class GroupedOutputPlugin:
    """Plugin to group parametrized test output by parent test function.

    Configuration is done via pytest command-line options.
    """

    def __init__(self, config):
        self.config = config
        self.current_group = None

        # Get configuration from pytest options; support multiple
        # module patterns separated by commas
        self.module_patterns = [
            p.strip()
            for p in config.option.scripttest_grouped_modules.split(',')]
        self.output_format = config.option.scripttest_grouped_output

    def _is_grouped_test(self, nodeid):
        """Check if the test should be grouped based on module patterns."""
        basename = nodeid.split('::')[0].split('/')[-1]
        return any(fnmatch.fnmatch(basename, pattern)
                   for pattern in self.module_patterns)

    def _format_group_name(self, group_id):
        """Format the group name based on output_format setting.

        group_id format: file.py::test_func
        """
        if self.output_format != 'short':
            return group_id

        file_part, func_part = group_id.rsplit('::', 1)

        # Remove prefixes (test_, scripttests_, scripttest_) and
        # suffixes (_yaml, _yml, _py), keeping a possible numeric suffix
        # added to make the function name unique
        func_part = re.sub(r'^(test_|scripttest_|scripttests_)+', '', func_part)
        func_part = re.sub(r'_(?:ya?ml|py)(_\d+)?$', r'\1', func_part)

        return f'{file_part}::{func_part}'

    def _extract_group_id(self, nodeid):
        """Extract the group identifier from a test nodeid.

        Format: file.py::test_func[param1-param2] or file.py::test_func
        Returns: file.py::test_func
        """
        parts = nodeid.split('::')
        if len(parts) >= 2:
            # Get function name without brackets
            func_part = parts[-1].split('[')[0]
            file_part = parts[0]
            return f'{file_part}::{func_part}'
        return None

    # tryfirst: run before the terminal reporter's hook, so that the
    # reporter does not write the module path before the group header
    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_logstart(self, nodeid, location):
        """Hook called when pytest is about to run a test."""
        # Only process tests matching the configured patterns
        if not self._is_grouped_test(nodeid):
            return

        # Get the group identifier
        group_id = self._extract_group_id(nodeid)

        # Print group header if it's a new group
        if group_id and group_id != self.current_group:
            self.current_group = group_id

            # Format the group name based on settings
            formatted_name = self._format_group_name(group_id)

            # Print group header via the terminal reporter, if in use
            # (not with -p no:terminal)
            reporter = self.config.pluginmanager.get_plugin(
                'terminalreporter')
            if reporter is not None:
                self._write_group_header(reporter, nodeid, formatted_name)

    def _write_group_header(self, reporter, nodeid, header):
        """Write group `header` for `nodeid` with terminal `reporter`.

        Mimic `TerminalReporter.write_fspath_result`, which writes the
        module path when the module changes: first fill the current
        line with progress information (if any), and then write the
        header on a new line. Also set the reporter's current module
        path, so that the reporter does not write it on a line of its
        own after the header. This relies on attributes and methods of
        `TerminalReporter` that are not part of the public pytest API;
        if they are missing, just write the header.
        """
        tw = self.config.get_terminal_writer()
        if (tw.width_of_current_line > 0
                and getattr(reporter, '_show_progress_info', False)
                and hasattr(reporter,
                            '_write_progress_information_filling_space')):
            reporter._write_progress_information_filling_space()
        if hasattr(reporter, 'currentfspath'):
            reporter.currentfspath = (
                self.config.rootpath / nodeid.split('::')[0])
        tw.line()
        tw.write(f'{header} ')


def pytest_addoption(parser):
    """Add command-line options for the grouped output plugin.

    Do nothing if the options have already been added to `parser`, so
    that this can be called both as a hook and explicitly from
    ``conftest.py``, also from several ``conftest.py`` files.
    """
    if parser in _option_parsers:
        return
    _option_parsers.add(parser)
    group = parser.getgroup('scripttestlib')
    group.addoption(
        '--scripttest-grouped-modules',
        metavar='PATTERNS',
        default='test_scripts*',
        help=('Glob pattern(s) of test modules to apply grouping to'
              ' (default: %(default)s). Use comma-separated values for'
              ' multiple patterns.')
    )
    group.addoption(
        '--scripttest-grouped-output',
        default='short',
        choices=['none', 'full', 'short'],
        help=('Format for test output when using grouped organization.'
              ' "short" (default) omits typical prefixes and suffixes'
              ' generated from scripttestlib test file names and shows'
              ' simplified names like "basename";'
              ' "full" shows complete test function names like'
              ' "test_scripttest_basename_yaml";'
              ' "none" disables grouping and uses standard pytest output.')
    )


def pytest_configure(config):
    """Register the grouped output plugin, unless already registered."""
    if config.pluginmanager.has_plugin('grouped_output'):
        return
    # Only activate at the default or reduced (-q) verbosity (with -v,
    # pytest shows each test on a line of its own) and when format is
    # not 'none'; the option "verbose" is missing with -p no:terminal
    if (getattr(config.option, 'verbose', 0) <= 0
            and config.option.scripttest_grouped_output != 'none'):
        config.pluginmanager.register(GroupedOutputPlugin(config),
                                      'grouped_output')
