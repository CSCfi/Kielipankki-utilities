
"""
vrt_drop_empty.py

The actual implementation of vrt-drop-empty.

Please run "vrt-drop-empty -h" for more information.
"""


import re
import sys

from collections import defaultdict
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
    ARGSPECS = [
        ('--verbose|-v',
         '''output the number of dropped structures to stderr''')
    ]

    def __init__(self):
        super().__init__()

    def main(self, args, inf, ouf):
        """Read inf, write to ouf, with command-line arguments args."""
        drop_counts = defaultdict(int)

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
                        drop_counts[struct] += 1
                elif not line.startswith(b'<!'):
                    # Start tag
                    struct = line[1:].partition(b' ')[0].rstrip(b'>\n')
                    struct_stack.append((struct, linenum))
            return (line for linenum, line in enumerate(lines)
                    if linenum not in drop_line_nums)

        def output_drop_counts():
            """Output the number of structures dropped."""
            if not drop_counts:
                sys.stderr.write('No structures dropped\n')
            else:
                sys.stderr.write('Dropped structures:\n')
                for struct in sorted(drop_counts.keys()):
                    sys.stderr.write(
                        f'  {struct.decode("UTF-8")}: {drop_counts[struct]}\n')

        LT = b'<'[0]
        for istag, lines in groupby(inf, lambda line: line[0] == LT):
            if istag:
                lines = drop_empty(list(lines))
            for line in lines:
                ouf.write(line)
        if args.verbose:
            output_drop_counts()
