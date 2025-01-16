
"""
vrt_select.py

The actual implementation of vrt-select.
"""


# TODO:
# - Add a VRT comment to the end of output with the number of kept and
#   dropped structures
# - Warn if dropping leaves an outer structure empty: e.g., if
#   dropping sentences leaves a paragraph or text empty
# - Keep tags of overlapping structures within dropped structures
#   (might not be easy)
# - Add option --find=regexp for substring matches (a shorthand for
#   --test=.*regexp.*). It is in principle simple, but the difficult
#   part is to require at least one --test or --find but allow both
#   (required but not mutually exclusive).


import re
import sys

from enum import Enum
from itertools import groupby

from vrtargsoolib import InputProcessor
from vrtcommentlib import makebinvrtcomment


class StructSelect(InputProcessor):

    """
    Select (keep or drop) from the VRT input structures with
    attribute values matching specified regular expressions.
    """

    DESCRIPTION = """
    Select (keep or drop) from the VRT input structures (elements)
    with attribute values matching specified regular expressions.
    """
    ARGSPECS = [
        ('--structure|--element|-s|-e = struct = "text" -> struct',
         'Select structures (elements) struct (default: %(default)s).'
         ' Any lines outside structs are output intact.'),
        ('#EXCLUSIVE',
         (
             ('--keep|-k -> keep',
              'Output the structures matching the tests (the default).',
              # The following arguments make this work: if this had
              # action='store_true', default=True and --drop had
              # target "!keep", --keep would get metavar KEEP, which
              # it should not
              dict(action='store_const', const=True, default=True)),
             ('--drop|-d -> keep',
              'Output the structures not matching the tests.',
              dict(action='store_const', const=False)),
         )),
        ('--test|-t = test -> tests',
         'Select (keep or drop) a structure if its attribute attrname'
         ' matches the (Python) regular expression regexp.'
         ' regexp needs to match in full, so use .* at the beginning and/or'
         ' end to allow substring matches.'
         ' If multiple tests are specified, the structure needs to match'
         ' either all of them (the default) or at least one of them (with'
         ' --any).',
         dict(required=True,
              metavar='attrname=regexp',
              action='append')),
        ('#EXCLUSIVE',
         (
             ('--all -> all_tests',
              'All tests need to match (the default).',
              dict(action='store_const', const=True, default=True)),
             ('--any -> all_tests',
              'At least one test needs to match.',
              dict(action='store_const', const=False)),
         )),
        ('--comment|-c',
         'Add a VRT comment to the end of output with the number of'
         ' structures kept and dropped.'),
        ('--verbose|-v',
         'Write to stderr the number of structures kept and dropped.'),
    ]
    EPILOG = """
    Note that the tool does not warn if dropping structures leaves the
    enclosing structure empty. Also, if the input contains overlapping
    structures (such as pages), their start and end tags within
    dropped structures are removed even if they continued beyond a
    dropped structure.
    """

    def __init__(self):
        super().__init__()

    def check_args(self, args):
        super().check_args(args)
        tests = []
        for test in args.tests:
            attrname, _, regexp = test.partition('=')
            if '=' not in test or not attrname:
                self.error_exit(
                    f'Attribute test not of the form attrname=regexp: {test}')
            tests.append(
                (attrname.strip().encode(), re.compile(regexp.lstrip())))
        args.tests = tests

    def main(self, args, inf, ouf):

        LESS_THAN = b'<'[0]
        linenum = 1
        struct_begin = b'<' + args.struct.encode() + b' '
        struct_end = b'</' + args.struct.encode() + b'>'
        count = args.verbose or args.comment
        # test_func is a test function for attribute value matches
        test_func0 = all if args.all_tests else any
        test_func = test_func0 if args.keep else lambda x: not test_func0(x)
        tests = args.tests

        def make_attrdict(line):
            # TODO: This could perhaps be optimized for a single
            # attribute test by having a separate function to extract
            # only the value of a single attribute and by choosing the
            # function to use in advance
            return dict((name, val) for name, val
                        in re.findall(rb' ([\w-]+)="(.*?)"', line))

        def keep_struct(struct_line):
            """Return true if struct_line begins a structure to be kept."""
            attrdict = make_attrdict(struct_line)
            return test_func(
                regexp.fullmatch(attrdict.get(attrname, b'').decode())
                for attrname, regexp in tests)

        struct_count = 0
        keep_count = 0
        in_struct = False
        keep = True
        for line in inf:
            linenum += 1
            if line[0] == LESS_THAN:
                if line.startswith(struct_begin):
                    keep = keep_struct(line)
                    if count:
                        struct_count += 1
                        if keep:
                            keep_count += 1
                    in_struct = True
                elif line.startswith(struct_end):
                    in_struct = False
            if keep:
                ouf.write(line)
            # Keep all lines outside the structures to be selected
            if not in_struct:
                keep = True
        if count:
            infomsg = (
                f'{struct_count} {args.struct} structures in input,'
                f' kept {keep_count}, dropped {struct_count - keep_count}')
            if args.comment:
                ouf.write(makebinvrtcomment(
                    b'info', b'vrt-select: ' + infomsg.encode()))
            if args.verbose:
                sys.stderr.write(infomsg + '\n')
