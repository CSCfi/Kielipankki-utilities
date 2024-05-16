
"""
vrt_drop_empty.py

The actual implementation of vrt-drop-empty.

Please run "vrt-drop-empty -h" for more information.
"""


import re

from itertools import groupby

from vrtargsoolib import InputProcessor


class VrtEmptyStructDropper(InputProcessor):

    """Class implementing vrt-drop-empty functionality."""

    DESCRIPTION = """
    Drop (remove) empty structures (elements) from the input VRT, that
    is, structures containing no tokens. Such structures cannot be
    represented in CWB data and are ignored by cwb-encode. XML-style
    comment lines within empty structures are retained.
    """

    def __init__(self):
        super().__init__()

    def main(self, args, inf, ouf):
        """Read inf, write to ouf, with command-line arguments args."""

        def drop_empty(lines):
            """Return generator iterating over lines not forming empty struct."""
            struct_stack = []
            drop_line_nums = set()
            for linenum, line in enumerate(lines):
                if line.startswith(b'</'):
                    # End tag
                    struct = line[2:-2]
                    if struct_stack and struct_stack[-1][0] == struct:
                        drop_line_nums.add(linenum)
                        drop_line_nums.add(struct_stack[-1][1])
                        struct_stack.pop()
                elif not line.startswith(b'<!'):
                    # Start tag
                    struct = line[1:].partition(b' ')[0].rstrip(b'>\n')
                    struct_stack.append((struct, linenum))
            return (line for linenum, line in enumerate(lines)
                    if linenum not in drop_line_nums)

        LT = b'<'[0]
        for istag, lines in groupby(inf, lambda line: line[0] == LT):
            if istag:
                lines = drop_empty(list(lines))
            for line in lines:
                ouf.write(line)
