
"""
Pytest plugin for grouped parametrized test output.

This plugin provides a custom reporter that groups the output of parametrized
tests by their parent test function, making it clearer which function's tests
are currently running.

By default, this plugin is specifically designed for scripttestlib-based tests
but can be configured to apply to other test modules.

Usage:
------
Either register it in pytest.ini or conftest.py:
    pytest_plugins = ["scripttestlib.pytest_grouped_output"]

Configuration via command-line options:
    --grouped-output-modules=PATTERN
          Glob patterns of test modules to group (default: test_scripts*)
    --grouped-output-format=FORMAT
          Output format: 'short' (default), 'full' or 'none':
          'short': Simplified names (removes prefixes/suffixes)
          'full': Complete function names
          'none': Disable grouping, use standard pytest output

Example output with default settings (short format):
    test_scripts_grouped.py
    test_scripts_grouped.py::hrt_encode_tags ............................ [ 12%]
    .................................................................
    test_scripts_grouped.py::vrt_drop_attrs ............................. [ 45%]
    .................................................................

With --grouped-output-format=full:
    test_scripts_grouped.py
    test_scripts_grouped.py::test_scripttest_hrt_encode_tags_yaml ....... [ 12%]
    ..................................................................
    test_scripts_grouped.py::test_scripttest_vrt_drop_attrs_yaml ........ [ 45%]
    ..................................................................

With --grouped-output-format=none:
    Uses standard pytest output (no grouping headers)

Implementation:
    This plugin uses pytest's public hook API (pytest_runtest_logstart) to
    intercept test runs and insert group headers. The terminal writer is
    obtained via the public get_terminal_writer() method.
"""


import fnmatch
import re


class GroupedOutputPlugin:
    """Plugin to group parametrized test output by parent test function.

    Configuration is done via pytest command-line options.
    """

    def __init__(self, config):
        self.config = config
        self.current_group = None

        # Get configuration from pytest options
        self.modules_pattern = getattr(config.option, 'grouped_output_modules',
                                       'test_scripts*')
        self.output_format = getattr(config.option, 'grouped_output_format',
                                     'short')

    def _is_grouped_test(self, nodeid):
        """Check if the test should be grouped based on module patterns."""
        # If format is 'none', disable grouping entirely
        if self.output_format == 'none':
            return False

        parts = nodeid.split('::')
        if not parts:
            return False

        module_part = parts[0]
        basename = module_part.split('/')[-1]

        # Support multiple patterns separated by comma
        patterns = [p.strip() for p in self.modules_pattern.split(',')]
        for pattern in patterns:
            if fnmatch.fnmatch(basename, pattern):
                return True
        return False

    def _format_group_name(self, group_id):
        """Format the group name based on output_format setting.

        group_id format: file.py::test_func
        """
        if self.output_format != 'short':
            return group_id

        # Extract just the function name
        if '::' not in group_id:
            return group_id

        file_part, func_part = group_id.rsplit('::', 1)

        # Remove prefixes (test_, scripttests_, scripttest_) and
        # suffixes (_yaml, _py) using a single regex replacement
        func_part = re.sub(r'^(test_|scripttest_|scripttests_)+', '', func_part)
        func_part = re.sub(r'(_yaml|_py)$', '', func_part)

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

            # Print group header using the terminal writer
            tw = self.config.get_terminal_writer()
            tw.write(f'\n{formatted_name} ')


def pytest_addoption(parser):
    """Add command-line options for the grouped output plugin."""
    group = parser.getgroup('grouped output')
    group.addoption(
        '--grouped-output-modules',
        default='test_scripts*',
        help=('Glob pattern(s) of test modules to apply grouping to'
              ' (default: test_scripts*). Use comma-separated values for'
              ' multiple patterns.')
    )
    group.addoption(
        '--grouped-output-format',
        default='short',
        choices=['none', 'full', 'short'],
        help=('Format for test output when using grouped organization.'
              ' "short" (default) shows simplified names like "vrt_drop_attrs",'
              ' "full" shows complete names like'
              ' "test_scripttest_vrt_drop_attrs_yaml",'
              ' "none" disables grouping and uses standard pytest output.')
    )


def pytest_configure(config):
    """Register the grouped output plugin."""
    # Only activate in non-verbose mode and when format is not 'none'
    if (not config.option.verbose
            and config.option.grouped_output_format != 'none'):
        config.pluginmanager.register(GroupedOutputPlugin(config),
                                      'grouped_output')
