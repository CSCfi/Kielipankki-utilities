
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
        charcount_posattr = b'charcount'
        struct_stack = []
        lines = []
        struct_counts = defaultdict(lambda: defaultdict(int))
        token_counts = defaultdict(lambda: defaultdict(int))
        # Structure start line number in lines
        struct_start_linenums = defaultdict(int)
        struct = None
        attrnum_word = 0
        token_split_count = attrnum_word + 1

        def get_attrnum_word(pos_attrs, linenr):
            """Get the number of attribute ``word`` in `pos_attrs`.

            `linenr` is used only in a possible error message.
            """
            try:
                wordnum = pos_attrs.index(b'word')
            except ValueError:
                self.error_exit('positional-attributes comment without "word"',
                                filename=inf.name, linenr=linenr + 1)
            return wordnum

        def isword(word):
            """Return True if word contains a Unicode-alpahnumeric char."""
            return any(c.isalnum() for c in word)

        def append_count_attrs(line, struct, struct_counts, token_counts):
            """Append count attrs from counts to `struct` start tag `line`."""
            # print(line, struct, struct_counts, token_counts)
            attrs = ([(name + b'_count', count)
                      for name, count in struct_counts[struct].items()
                      if count > 0]
                     + [(name + b'_count', count)
                        for name, count in token_counts[struct].items()]
                     + [(b'num_in_' + ancestor, struct_counts[ancestor][struct])
                        for ancestor in struct_counts
                        if (ancestor != struct
                            and struct_counts[ancestor][struct] > 0)])
            line_end = b' '.join(
                name + b'="' + str(value).encode('utf-8') + b'"'
                for name, value in attrs)
            # print(line_end)
            return line.replace(b'>\n', b' ' + line_end + b'>\n')

        for linenr, line in enumerate(inf):
            if ml.ismeta(line):
                if ml.isstarttag(line):
                    struct = ml.element(line)
                    if not struct_stack:
                        # Count top-level structures within the input
                        struct_counts[b'corpus'][struct] += 1
                        if lines:
                            # New top-level structure; output previous one
                            ouf.writelines(lines)
                            lines = []
                    lines.append(line)
                    struct_start_linenums[struct] = len(lines) - 1
                    for containing_struct in struct_stack:
                        # Increment the number of this kind of struct
                        # in the containing structs
                        struct_counts[containing_struct][struct] += 1
                    struct_stack.append(struct)
                elif ml.isendtag(line):
                    lines.append(line)
                    closing_struct = ml.element(line)
                    if closing_struct != struct:
                        self.error_exit(
                            f'expected </{struct.decode("utf-8")}>,'
                            f' got </{closing_struct.decode("utf-8")}>',
                            filename=inf.name, linenr=linenr + 1)
                    struct_stack.pop()
                    start_linenum = struct_start_linenums[struct]
                    lines[start_linenum] = append_count_attrs(
                        lines[start_linenum], closing_struct, struct_counts,
                        token_counts)
                    if struct_stack:
                        struct = struct_stack[-1]
                        for key in token_counts[closing_struct]:
                            token_counts[struct][key] += (
                                token_counts[closing_struct][key])
                    else:
                        struct = None
                    struct_counts[closing_struct].clear()
                    token_counts[closing_struct].clear()
                elif nl.isnameline(line):
                    pos_attrs = nl.parsenameline(line)
                    attrnum_word = get_attrnum_word(pos_attrs, linenr)
                    token_split_count = attrnum_word + 1
                    lines.append(
                        nl.makenameline(pos_attrs + [charcount_posattr]))
                else:
                    lines.append(line)
            else:
                # Token line
                token_counts[struct][b'token'] += 1
                word = (line[:-1].split(b'\t', token_split_count)[attrnum_word]
                        .decode('utf-8'))
                # int + bool is faster than int + int(bool)
                token_counts[struct][b'word'] += isword(word)
                wordlen = len(word)
                token_counts[struct][b'char'] += wordlen
                lines.append(line[:-1] + b'\t' + str(wordlen).encode('utf-8')
                             + b'\n')
        if lines:
            ouf.writelines(lines)
