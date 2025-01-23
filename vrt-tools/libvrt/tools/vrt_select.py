
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
import libvrt.metaline as ml


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
         '''Select structures (elements) struct (default: %(default)s).
            Any lines outside structs are output intact.'''),
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
         '''Select (keep or drop) a structure if the value of its
            attribute attrname matches the (Python) regular expression
            regexp or any line in file filename. If filename is preceded by
            *, treat the lines as regular expressions, otherwise as literal
            strings.
            ! immediately before = negates the test.
            regexp and regular expressions read from filename need to match
            in full, so use .* at the beginning and/or end to allow
            substring matches.
            Leading and trailing whitespace is removed from attrname, regexp
            and filename but preserved in strings and regular expressions
            read from file filename. To make regexp match a leading or
            trailing space, use e.g. \\s or \\x20.
            Characters < > & " should be XML-encoded as &lt; &gt; &amp;
            &quot; in regular expressions and string values, as in VRT
            attribute values.
            If multiple tests are specified, the structure needs to match
            either all of them (the default) or at least one of them (with
            --any).''',
         dict(required=True,
              metavar='attrname[!]=(regexp|<[*]filename)',
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
         '''Add a VRT comment to the end of output with the number of
            structures kept and dropped.'''),
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

        def read_file(fname, values=None, add_fn=None):
            """Return values read from file fname, items added with add_fn.

            Each line (with possible trailing newline removed) in
            fname is added to values with add_fn.
            If values is None, it defaults to an empty list.
            add_fn is used to add items to values (default: append to
            list).
            Exit with an error message if file fname cannot be read.
            """
            if values is None:
                values = []
                add_fn = None
            if add_fn is None:
                add_fn = lambda vals, x: vals.append(x)
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    for line in f:
                        add_fn(values, line.rstrip('\n'))
            except IOError as e:
                self.error_exit(f'Error reading file {fname}: {e}')
            return values

        def make_regexp_test(attrname, regexp):
            """Return function for testing if value of attrname matches regexp.

            The returned function takes an attribute dictionary
            attrdict as its argument and tests if attrdict[attrname]
            fully matches regexp.
            """
            compiled_re = re.compile(regexp)

            def match(attrdict):
                # TODO?: Decode attribute value only once even if used
                # in multiple tests. However, having multiple tests
                # for a single attribute may be a relatively rare use
                # case.
                return compiled_re.fullmatch(
                    attrdict.get(attrname, b'').decode())

            return match

        def make_file_test(attrname, fname):
            """Return function for testing if value of attrname is in fname.

            The returned function takes an attribute dictionary
            attrdict as its argument and tests if attrdict[attrname]
            exactly matches any line read from file fname.
            """
            values = read_file(fname, set(), lambda vals, x: vals.add(x))

            def test(attrdict):
                return attrdict.get(attrname, b'').decode() in values

            return test

        def make_regexp_file_test(attrname, fname):
            """Return function to test if value of attrname matches RE in fname.

            The returned function takes an attribute dictionary
            attrdict as its argument and tests if attrdict[attrname]
            fully matches any regular expression read from file fname
            (each line is treated as a single regular expression).
            """
            return make_regexp_test(attrname, '|'.join(read_file(fname)))

        super().check_args(args)
        tests = []
        for test in args.tests:
            attrname, _, value = test.partition('=')
            if '=' not in test or not attrname:
                self.error_exit(
                    f'Attribute test not of the form'
                    f' attrname[!]=(regexp|<[*]filename): {test}')
            value = value.strip()
            if value.startswith('<*'):
                make_test = make_regexp_file_test
                value = value[2:]
            elif value and value[0] == '<':
                make_test = make_file_test
                value = value[1:]
            else:
                make_test = make_regexp_test
            negate = False
            if attrname[-1] == '!':
                negate = True
                attrname = attrname[:-1]
            test_func = make_test(attrname.strip().encode(), value.strip())
            if negate:
                test_func = lambda attrdict, tf=test_func: not tf(attrdict)
            tests.append(test_func)
        args.tests = tests

    def main(self, args, inf, ouf):

        LESS_THAN = b'<'[0]
        linenum = 1
        struct_begin = b'<' + args.struct.encode() + b' '
        struct_end = b'</' + args.struct.encode() + b'>'
        count = args.verbose or args.comment
        # combine_tests is a function combining tests for attribute
        # value matches
        # TODO?: Lazily evaluate the tests. It would require all- and
        # any-like functions that would take functions as arguments
        # and call them only until one returns False (all) or True
        # (any). However, it would improve performance only with
        # multiple tests, which may be a rarer use case than a single
        # test.
        combine_tests_base = all if args.all_tests else any
        combine_tests = (combine_tests_base if args.keep
                         else lambda tests: not combine_tests_base(tests))
        tests = args.tests

        def make_attrdict(line):
            # TODO: This could perhaps be optimized for a single
            # attribute test by having a separate function to extract
            # only the value of a single attribute and by choosing the
            # function to use in advance
            return ml.mapping(line)

        def keep_struct(struct_line):
            """Return true if struct_line begins a structure to be kept."""
            attrdict = make_attrdict(struct_line)
            return combine_tests(test(attrdict) for test in tests)

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
