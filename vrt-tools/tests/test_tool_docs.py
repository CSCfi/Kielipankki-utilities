"""
test_tool_docs.py

Pytest test checking that the Markdown documentation of VRT tools in
docs/tools/ is up to date with the usage information of the tools.
"""


import os
import subprocess


_VRTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPT = os.path.join(_VRTDIR, 'docs', 'make-tool-docs')


def test_tool_docs_up_to_date():
    """Test that docs/tools/*.md are up to date."""
    result = subprocess.run([_SCRIPT, '--check'], capture_output=True,
                            text=True)
    assert result.returncode == 0, (
        'Tool documentation is out of date; please run docs/make-tool-docs\n'
        + result.stdout + result.stderr)
