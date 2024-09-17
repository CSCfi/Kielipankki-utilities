
"""
vrt_add_counts.py

The actual implementation of vrt-add_counts.

Please run "vrt-add-counts -h" for more information.
"""


import sys
import re

from collections import defaultdict, OrderedDict

from libvrt import metaline as ml
from libvrt import nameline as nl

from vrtargsoolib import InputProcessor


class VrtCountAdder(InputProcessor):

    """Class implementing vrt-add-counts functionality."""

    DESCRIPTION = """
    Add structural attributes (annotations) to the input VRT with
    information on the number of inner structures, tokens and words,
    and the number of the structure within the containing structure.
    """
    ARGSPECS = [
    ]

    def __init__(self):
        # extra_types=... is needed for using module-level functions
        # as types in ARGSPECS (otherwise, type could be passed via a
        # dict)
        super().__init__(extra_types=globals())

    def check_args(self, args):
        """Check and modify `args` (parsed command line arguments)."""
        super().check_args(args)

    def main(self, args, inf, ouf):
        """Read `inf`, write to `ouf`, with command-line arguments `args`."""
        struct_stack = []
        lines = []
        counts = defaultdict(lambda: defaultdict(int))
        # Structure start line number in lines
        struct_start_linenums = defaultdict(int)
        struct = None
        attrnum_word = 0
        token_split_count = attrnum_word + 1

        def get_attrnum_word(line, linenr):
            """Get the number of attr "word" in pos-attrs comment `line`."""
            pos_attrs = nl.parsenameline(line)
            try:
                wordnum = pos_attrs.index(b'word')
            except ValueError:
                self.error_exit('positional-attributes comment without "word"',
                                filename=inf.name, linenr=linenr + 1)
            return wordnum

        def isword(word):
            """Return True if word contains a Unicode-alpahnumeric char."""
            return any(c.isalnum() for c in word.decode('utf-8'))

        def append_count_attrs(line, counts):
            """Append count attributes from `counts` to start tag `line`."""
            line_end = b''.join(
                b' ' + name + b'_count="' + str(count).encode('utf-8') + b'"'
                for name, count in counts.items())
            return line.replace(b'>\n', line_end + b'>\n')

        for linenr, line in enumerate(inf):
            lines.append(line)
            if ml.ismeta(line):
                if ml.isstarttag(line):
                    struct = ml.element(line)
                    struct_start_linenums[struct] = len(lines) - 1
                    if struct_stack:
                        # Increment the number of this kind of struct
                        # in the containing struct
                        counts[struct_stack[-1]][struct] += 1
                    struct_stack.append(struct)
                elif ml.isendtag(line):
                    closing_struct = ml.element(line)
                    if closing_struct != struct:
                        self.error_exit(
                            f'expected </{struct.decode("utf-8")}>,'
                            f' got </{closing_struct.decode("utf-8")}>',
                            filename=inf.name, linenr=linenr + 1)
                    struct_stack.pop()
                    start_linenum = struct_start_linenums[struct]
                    lines[start_linenum] = append_count_attrs(
                        lines[start_linenum], counts[closing_struct])
                    if struct_stack:
                        struct = struct_stack[-1]
                        for key, count in counts[closing_struct].items():
                            counts[struct][key] += count
                    else:
                        struct = None
                        ouf.writelines(lines)
                        lines = []
                    counts[closing_struct].clear()
                elif nl.isnameline(line):
                    attrnum_word = get_attrnum_word(line, linenr)
                    token_split_count = attrnum_word + 1
            else:
                counts[struct][b'token'] += 1
                word = line[:-1].split(b'\t', token_split_count)[attrnum_word]
                # int + bool is faster than int + int(bool)
                counts[struct][b'word'] += isword(word)
