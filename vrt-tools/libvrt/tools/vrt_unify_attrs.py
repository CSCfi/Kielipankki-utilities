
"""
vrt_unify_attrs.py

The actual implementation of vrt-unify-attrs.

Please run "vrt-unify-attrs -h" for more information.
"""


import sys
import re

from argparse import ArgumentTypeError
from collections import defaultdict, OrderedDict
from tempfile import NamedTemporaryFile

from libvrt import metaline as ml
from libvrt.iterutils import find_duplicates
from libvrt.argtypes import (
    encode_utf8,
    attrlist,
    attr_regex_list_combined,
    attr_regex_list_combined_value)
from libvrt.seekable import get_seekable

from vrtargsoolib import InputProcessor


class VrtStructAttrUnifier(InputProcessor):

    """Class implementing vrt-unify-attrs functionality."""

    DESCRIPTION = """
    Unify the structural attributes (annotations) in the input VRT:
    add attributes possibly missing from some structures (elements)
    and sort the attributes to the same order in all structures
    (alphabetically be default).
    """
    EPILOG = """
    The tool reads the input twice unless --single-pass is specified.
    If the input is not a file, the tool writes the input to a
    temporary file for the second pass.
    """
    ARGSPECS = [
        ('--single-pass',
         '''read the input only once and output the attributes specified with
            --always (or --exactly)'''),
        ('#GROUPED structure-specific options',
         '''The following options can be specified multiple times: each
            occurrence applies to the --structure after which it is
            specified. If an option is specified before any --structure, it
            becomes the default for all structures.''',
         [
             ('--structure|element|e = struct:encode_utf8',
              '''the options following this (up to the next --structure)
                 apply to structures struct'''),
             ('--default = ""',
              '''Add missing attributes with value str (default: "").
                 attr-regex-list is a list of attribute name regular
                 expressions, separated by spaces or commas.
                 If attr-regex-list is specified, apply to
                 attributes whose names fully match one of the
                 regular expressions in it, otherwise to all attributes.
                 If attr-regex-list is omitted, the colon following it can
                 also be omitted unless str contains a colon.
                 If the option is specified multiple times with different
                 attribute regular expressions, an attribute gets the str
                 specified for the last regular expression matching the
                 attribute name.''',
              dict(action='append',
                   type=attr_regex_list_combined_value,
                   silent_default=[],
                   metavar='[[attr-regex-list]:]str')),
             ('--input-order',
              '''order attributes to the order first encountered in input,
                 instead of sorting alphabetically; attributes encountered
                 only later are appended'''),
             ('--first = attrlist:attrlist',
              '''order attributes listed in attrlist before other attributes;
                 attributes in attrlist separated by spaces or commas,
                 duplicates not allowed''',
              # The processed value is a list, even though the option
              # can be specified only once (for each structure)
              dict(silent_default=[])),
             ('--last = attrlist:attrlist',
              '''order attributes listed in attrlist after other attributes,
                 attrlist value as for --first; attrlist may not contain any
                 attribute specified for --first''',
              dict(silent_default=[])),
             ('--always = attrlist:attrlist',
              '''always output attributes listed in attrlist, even if they
                 did not occur in the input; with --input-order, non-occurring
                 attributes are appended after occurring ones in the order
                 specified in attrlist, unless also listed in --first or
                 --last; attrlist value as for --first and --last''',
              dict(silent_default=[])),
             # No (silent_)default for --only, as a specified empty
             # value has a special meaning different from not
             # specifying the option at all
             ('--only = attr-regex-list:attr_regex_list_combined',
              '''output only attributes whose names fully match a regular
                 expression in attr-regex-list and which occur in
                 input, in addition to those possibly listed with --always;
                 an empty value (and no --always) removes all attributes'''),
             ('--exactly = attrlist:attrlist',
              '''always output only attributes listed in attrlist, shorthand
                 for --always=attrlist --only=attrlist; overrides the values
                 for --always and --only (but structure-specific --always and
                 --only override global --exactly)'''),
             ('--optional = attr-regex-list:attr_regex_list_combined',
              '''do not add attributes fully matching a regular expression in
                 attr-regex-list to structures from which they are missing
                 (unless listed with --always); has no effect with
                 --single-pass'''),
             ('--drop = attr-regex-list:attr_regex_list_combined',
              '''drop (remove) attributes fully matching a regular expression
                 in attr-regex-list (and not listed with --always, --only or
                 --exactly)'''),
         ]),
    ]

    def __init__(self):
        # extra_types=... is needed for using module-level functions
        # as types in ARGSPECS (otherwise, type could be passed via a
        # dict)
        super().__init__(extra_types=globals())

    def check_args(self, args, struct=None):
        """Check and modify args (parsed command line arguments).

        The method is called recursively for structure-specific
        arguments with struct as the structure name.
        """

        def check_first_last_dupls(args, struct=None):
            """If args.first and args.last contain same attrs, error exit.

            If struct is a string, mention it in the error message.
            """
            dupls = find_duplicates(args.first, args.last)
            suffix = f' (structure {struct.decode("UTF-8")})' if struct else ''
            if dupls:
                self.error_exit(
                    'error: same attributes in both --first and --last'
                    + f'{suffix}: '
                    + ', '.join(dupl.decode('UTF-8') for dupl in dupls),
                    exitcode=2)

        def convert_exactly(args, struct=None):
            """Convert --exactly to --always --only.

            Warn if also --always or --only has been specified.
            """
            if args.exactly is not None:
                warn_fmt = (
                    '--exactly overrides {}'
                    + (f' (structure {struct.decode("UTF-8")})' if struct
                       else ''))
                # --always=a --exactly=b -> exactly overrides, warn
                # --always=a --struct=x --exactly=b -> structure-specific
                #   overrides, do not warn
                # --exactly=b --struct=x --always=a -> structure-specific
                #   overrides, do not warn
                if 'exactly' in args._explicit:
                    if args.always and 'always' in args._explicit:
                        self.warn(warn_fmt.format('--always'))
                    if args.only is not None and 'only' in args._explicit:
                        self.warn(warn_fmt.format('--only'))
                    args.always = args.exactly.copy()
                    args.only = re.compile(b'|'.join(args.exactly))

        if struct is None:
            super().check_args(args)
        check_first_last_dupls(args, struct)
        convert_exactly(args, struct)
        # Process structure-specific arguments
        if struct is None:
            for struct2, struct_args in args.structure.items():
                self.check_args(struct_args, struct2)
            if args.single_pass:
                if args.optional or any(
                        struct_args.optional
                        for struct_args in args.structure.values()):
                    self.warn('--optional has no effect with --single-pass')

    def main(self, args, inf, ouf):
        """Read inf, write to ouf, with command-line arguments args."""

        # Attribute names occurring in each structure; use OrderedDict
        # (keys only) instead of a dict to be able to retain original
        # order with --input-order
        struct_attrs = defaultdict(OrderedDict)

        def getarg(name, struct):
            """Return the value for argument `name` for structure `struct`.

            If --structure=struct has not been specified, use the
            default value for `name` in `args`.
            """
            return getattr(args.structure.get(struct), name,
                           getattr(args, name))

        def orddict(iter_):
            """Return OrderedDict, keys from iterable iter_, values None."""
            return OrderedDict((item, None) for item in iter_)

        def collect_attrs(inf):
            """Read inf and collect structural attributes."""
            if args.single_pass:
                # If --single-pass, do not collect attributes but use
                # the attributes listed in --always
                for struct, struct_args in args.structure.items():
                    struct_attrs[struct] = (
                        OrderedDict((name, None)
                                    for name in struct_args.always))
                return
            for line in inf:
                if ml.ismeta(line) and ml.isstarttag(line):
                    add_attrs(line)

        def add_attrs(line):
            """Add attributes from start tag line to struct_attrs."""
            struct = ml.element(line)
            attrs = orddict(name for name, _ in ml.pairs(line))
            struct_attrs[struct].update(attrs)

        def unify_attrs(inf):
            """Write inf to ouf, structural attributes unified and sorted."""
            attrs_info = make_attrs_info()
            for line in inf:
                if ml.ismeta(line) and ml.isstarttag(line):
                    line = order_attrs(line, attrs_info)
                ouf.write(line)

        def make_attrs_info():
            """Return attribute info dict for each structure.

            Return dict[str, dict]: for each structure, the order of
            attributes and default values for each attribute.
            """

            attrs_info = {}

            def add_attr_info(struct, attrs):
                """Set attrs_info values for struct with attrs."""
                nonlocal attrs_info
                attrs_info[struct] = make_attr_info(struct, attrs)

            if args.single_pass:
                for struct, struct_args in args.structure.items():
                    add_attr_info(struct, orddict(struct_args.always or []))
                add_attr_info(None, orddict(args.always or []))
            else:
                for struct, attrs in struct_attrs.items():
                    add_attr_info(struct, attrs)
            return attrs_info

        def make_attr_info(struct, attrs):
            """Return attribute info dict for struct with attrs."""
            return {
                'order': make_order(struct, attrs),
                'default': make_default(struct, attrs),
                'optional': make_optional(struct, attrs),
            }

        def make_order(struct, attrs):
            """Return list containing order of attrs for struct."""
            opts = dict(
                (name, getarg(name, struct))
                for name in ['input_order', 'first', 'last', 'always', 'only',
                             'drop'])
            if opts['only'] is not None:
                attrs = orddict(attr for attr in attrs.keys()
                                if opts['only'].fullmatch(attr))
            elif opts['drop'] is not None:
                attrs = orddict(attr for attr in attrs.keys()
                                if not opts['drop'].fullmatch(attr))
            sortfn = (lambda x: x) if opts['input_order'] else sorted
            attrs.update(dict((attr, None) for attr in opts['always']))
            attrs = sortfn(list(attrs.keys()))
            order = [attr for attr in opts['first'] if attr in attrs]
            order.extend(
                attr for attr in attrs
                if attr not in opts['first'] and attr not in opts['last'])
            order.extend(attr for attr in opts['last'] if attr in attrs)
            return order

        def make_default(struct, attrs):
            """Return dict with default value for all attrs in struct."""
            default = {}
            default_vals = getarg('default', struct)
            for attr in list(attrs) + (getarg('always', struct) or []):
                # The last matching regexp specificies the default
                for regex, value in reversed(default_vals):
                    if regex.fullmatch(attr):
                        default[attr] = value
                        break
            return default

        def make_optional(struct, attrs):
            """Return set containing attrs matching --optional for struct. """
            optional_re = getarg('optional', struct)
            if not optional_re:
                return set()
            always = getarg('always', struct) or []
            return set(attr for attr in attrs
                       if attr not in always and optional_re.fullmatch(attr))

        def order_attrs(line, attrs_info):
            """Return start tag line, attributes according to attrs_info.

            attrs_info dict contains for each structure the order (a
            list of attribute names in the desired order) and defaults
            (a dict mapping attribute names to their default values).
            """
            struct = ml.element(line)
            attrs = ml.mapping(line)
            attr_info = attrs_info.get(struct) or attrs_info.get(None)
            default = attr_info['default']
            order = attr_info['order']
            optional = attr_info['optional']
            return ml.starttag(
                struct, ((name, attrs.get(name, default.get(name, b'')))
                         for name in order
                         if name in attrs or name not in optional))

        if not args.single_pass:
            # If the original input is not seekable, wrap it to appear
            # such
            inf = get_seekable(inf)
        # CHECK: Is this with statement needed? Does it work correctly
        # regardless of whether inf is the original inf or made
        # seekable?
        with inf as inf:
            # Pass 1: Read input, collecting structural attribute
            # names; if --single-pass, take attributes from --always
            collect_attrs(inf)
            # Pass 2: Reread input (original or temporary copy) and
            # write output with attribute names unified and sorted
            if not args.single_pass:
                inf.seek(0)
            unify_attrs(inf)
