
"""
vrt_drop_attrs.py

The actual implementation of vrt-drop-attrs.

Please run "vrt-drop-attrs -h" for more information.
"""


import sys
import re

from collections import defaultdict, OrderedDict

from libvrt import metaline as ml
from libvrt.argtypes import encode_utf8, attr_regex_list_combined

from vrtargsoolib import InputProcessor


class VrtStructAttrDropper(InputProcessor):

    """Class implementing vrt-drop-attrs functionality."""

    DESCRIPTION = """
    Drop (remove) the structural attributes (annotations) in the input
    VRT whose name matches a specified regular expression.
    """
    ARGSPECS = [
        ('--verbose|v',
         '''output to stderr the number of attributes dropped by structure'''),
        ('#GROUPED structure-specific options',
         '''The following options can be specified multiple times: each
            occurrence applies to the --structure after which it is
            specified. If an option is specified before any --structure, it
            becomes the default for all structures.''',
         [
             ('--structure|element|e = struct:encode_utf8',
              '''the options following this (up to the next --structure)
                 apply to structures struct'''),
             ('--drop = attr-regex-list:attr_regex_list_combined',
              '''drop attributes whose names fully match a regular
                 expression in attr-regex-list (separated by commas or
                 spaces) and are not matched by a regular expression
                 specified with --keep''',
              dict(silent_default=attr_regex_list_combined(''))),
             ('--keep = attr-regex-list:attr_regex_list_combined',
              '''keep attributes whose names fully match a regular
                 expression in attr-regex-list even if they were
                 matched by a regular expression specified with --drop''',
              dict(silent_default=attr_regex_list_combined(''))),
         ]),
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

        # Attribute names by structure name, already tested to be
        # dropped or kept: value 1 = drop, 2 = keep. These values
        # instead of False and True make it simpler and faster(?) to
        # handle the case in which an attribute name is not found in
        # the dict (in drop_attrs), as we can use an "or" expression
        # for that, evaluated only if the attribute is not in
        # keep_attr, regardless of its value.
        keep_attr = defaultdict(dict)
        # The values of command-line options --drop and --keep by
        # structure name; if not explicitly specified, the default
        struct_args = defaultdict(dict)
        # Possibly drop attributes from all structures (global --drop)
        check_all_structs = 'drop' in getattr(args, '_explicit', set())
        # Structures from which to drop attributes explicitly
        check_structs = set(args.structure.keys())
        # The number of attributes dropped by structure and attribute;
        # output with --verbose
        drop_counts = defaultdict(lambda: defaultdict(int))

        def getarg(name, struct):
            """Return the value for argument `name` for structure `struct`.

            If --structure=struct has not been specified, use the
            default value for `name` in `args`.
            Cache the values in `struct_args`.
            """
            if struct not in struct_args[name]:
                struct_args[name][struct] = (
                    getattr(args.structure.get(struct), name, None)
                    or getattr(args, name))
            return struct_args[name][struct]

        def check_keep_attr(struct, attrname):
            """Check if `attrname` in `struct` should be kept or dropped.

            Return 1 if `attrname` should be dropped, 2 if kept. Also
            store the result to `keep_attr[struct][attrname]` for
            faster future reference.
            """
            drop = getarg('drop', struct)
            keep = getarg('keep', struct)
            # Possible None returned by fullmatch needs to be
            # converted to bool first, as int(None) raises TypeError;
            # "not not x" is somewhat faster than "bool(x)"
            result = int((drop and not drop.fullmatch(attrname))
                         or (keep and not not keep.fullmatch(attrname))) + 1
            keep_attr[struct][attrname] = result
            return result

        def attr_is_kept_base(struct, attrname):
            """Return `True` if `attrname` in `struct` should be kept."""
            return ((keep_attr[struct].get(attrname)
                     or check_keep_attr(struct, attrname)) - 1)

        def attr_is_kept_count(struct, attrname):
            """As `attr_is_kept_base` but increment count in `drop_counts`."""
            keep = attr_is_kept_base(struct, attrname)
            if not keep:
                drop_counts[struct][attrname] += 1
            return keep

        def drop_attrs(line):
            """Return start tag line `line` with attributes dropped.

            Drop attributes as specified with command-line options.
            """
            struct = ml.element(line)
            if check_all_structs or struct in check_structs:
                return ml.starttag(
                    struct, ((name, val) for name, val in ml.pairs(line)
                             if attr_is_kept(struct, name)))
            else:
                # If attributes are not to be removed from struct,
                # return line as is, since it is much faster
                return line

        def print_drop_counts():
            """Print to stderr the number of attributes dropped.

            Structures are printed in the order they are in the
            `drop_counts` dict, that is, for Python 3.8+, in the order
            of the first occurrence of the structure. Attributes are
            printed in alphabetical order.
            """
            if not drop_counts:
                sys.stderr.write('No attributes dropped\n')
            else:
                sys.stderr.write(
                    'Number of attributes dropped:\n'
                    'structure\tattribute\tcount\n')
                for struct in drop_counts.keys():
                    for attrname, count in sorted(drop_counts[struct].items()):
                        sys.stderr.write(
                            '\t'.join([struct.decode('UTF-8'),
                                       attrname.decode('UTF-8'),
                                       str(count)])
                            + '\n')

        # The attr_is_kept function to be used; depends on whether
        # --verbose is specified (print counts) or not
        attr_is_kept = attr_is_kept_count if args.verbose else attr_is_kept_base

        for line in inf:
            if ml.ismeta(line) and ml.isstarttag(line):
                line = drop_attrs(line)
            ouf.write(line)
        if args.verbose:
            print_drop_counts()
