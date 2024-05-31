
"""
vrt_unify_attrs.py

The actual implementation of vrt-unify-attrs.

Please run "vrt-unify-attrs -h" for more information.
"""


import sys
import re

from argparse import ArgumentTypeError
from collections import defaultdict, OrderedDict, Counter
from itertools import chain
from tempfile import NamedTemporaryFile

from libvrt import metaline as ml

from vrtargsoolib import InputProcessor


# TODO: Move the following functions to a library module


def encode_utf8(s):
    """Argument type function converting str s to UTF-8 bytes."""
    return s.encode('UTF-8')


def attrlist(s):
    """Argument type function for a list of unique attribute names.

    The attributes in str s can be separated by commas or spaces.
    Return a list of bytes.

    Raise ArgumentTypeError if the attribute list contains
    duplicates or if attribute names are invalid.
    """
    # Split by commas and spaces, and filter out empty strings
    attrs = [attr for attr in re.split(r'[,\s]+', s or '') if attr]
    for attr in attrs:
        if not re.fullmatch(r'[_a-z][_a-z0-9]*', attr):
            raise ArgumentTypeError(f'invalid attribute name: {attr}')
    dupls = _find_duplicates(attrs)
    if dupls:
        raise ArgumentTypeError(
            'duplicate attribute names: ' + ', '.join(dupls))
    return [attr.encode('UTF-8') for attr in attrs]


def _find_duplicates(*iters):
    """Return list of items occurring more than once in iterables *iters."""
    counts = Counter(chain(*iters))
    return [item for item, cnt in counts.items() if cnt > 1]


class VrtStructAttrUnifier(InputProcessor):

    """Class implementing vrt-unify-attrs functionality."""

    DESCRIPTION = """
    Unify the structural attributes (annotations) in the input VRT:
    add attributes possibly missing from some structures (elements)
    and sort the attributes alphabetically.
    """
    EPILOG = """
    If the input is not a file, the tool writes the input to a
    temporary file.
    """
    ARGSPECS = [
        ('#GROUPED structure-specific options',
         '''The following options can be specified multiple times: each
            occurrence applies to the --structure after which it is
            specified. If an option is specified before any --structure, it
            becomes the default for all structures.''',
         [
             ('--structure|element|e = struct:encode_utf8',
              '''the options following this (up to the next --structure)
                 apply to structures struct'''),
             ('--default = str:encode_utf8 ""',
              '''add missing attributes with value str'''),
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
             ('--only = attrlist:attrlist',
              '''output only attributes listed in attrlist (and occurring in
                 input or listed with --always); an empty value removes all
                 attributes'''),
             ('--exactly = attrlist:attrlist',
              '''always output only attributes listed in attrlist, shorthand
                 for --always=attrlist --only=attrlist; overrides the values
                 for --always and --only'''),
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
            dupls = _find_duplicates(args.first, args.last)
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
                if args.always:
                    self.warn(warn_fmt.format('--always'))
                if args.only is not None:
                    self.warn(warn_fmt.format('--only'))
                args.always = args.exactly.copy()
                args.only = args.exactly.copy()

        if struct is None:
            super().check_args(args)
        check_first_last_dupls(args, struct)
        convert_exactly(args, struct)
        # Process structure-specific arguments
        if struct is None:
            for struct2, struct_args in args.structure.items():
                self.check_args(struct_args, struct2)

    def main(self, args, inf, ouf):
        """Read inf, write to ouf, with command-line arguments args."""

        # Attribute names occurring in each structure; use OrderedDict
        # (keys only) instead of a dict to be able to retain original
        # order with --input-order
        struct_attrs = defaultdict(OrderedDict)
        # If the original input is not seekable, the input is copied
        # to a seekable temporary file. Python 3.6.8 on Puhti seems to
        # return seekable() == True for stdin, so also test for name
        # "<stdin>".
        write_tmp = not inf.seekable() or inf.name == '<stdin>'
        seekable_inf = NamedTemporaryFile(delete=False) if write_tmp else inf
        seekable_inf_name = seekable_inf.name

        def getarg(name, struct):
            """Return the value for argument `name` for structure `struct`.

            If --structure=struct has not been specified, use the
            default value for `name` in `args`.
            """
            return getattr(args.structure.get(struct), name,
                           getattr(args, name))

        def collect_attrs(inf, ouf_tmp):
            """Read inf, collect struct attrs; write to ouf_tmp if not None."""
            for line in inf:
                if ml.ismeta(line) and ml.isstarttag(line):
                    add_attrs(line)
                if ouf_tmp:
                    ouf_tmp.write(line)
            if ouf_tmp:
                ouf_tmp.close()

        def add_attrs(line):
            """Add attributes from start tag line to struct_attrs."""
            struct = ml.element(line)
            attrs = OrderedDict((name, None) for name, _ in ml.pairs(line))
            struct_attrs[struct].update(attrs)

        def unify_attrs(inf):
            """Write inf to ouf, structural attributes unified and sorted."""
            orders = make_orders()
            for line in inf:
                if ml.ismeta(line) and ml.isstarttag(line):
                    line = order_attrs(line, orders)
                ouf.write(line)

        def make_orders():
            """Return dict[list] containing attr order for each struct."""
            orders = {}
            for struct, attrs in struct_attrs.items():
                orders[struct] = make_order(struct, attrs)
            return orders

        def make_order(struct, attrs):
            """Return list containing order of attrs for struct."""
            opts = dict(
                (name, getarg(name, struct))
                for name in ['input_order', 'first', 'last', 'always', 'only'])
            if opts['only'] is not None:
                attrs = OrderedDict((attr, None) for attr in attrs.keys()
                                    if attr in set(opts['only']))
            sortfn = (lambda x: x) if opts['input_order'] else sorted
            attrs.update(dict((attr, None) for attr in opts['always']))
            attrs = sortfn(list(attrs.keys()))
            order = [attr for attr in opts['first'] if attr in attrs]
            order.extend(
                attr for attr in attrs
                if attr not in opts['first'] and attr not in opts['last'])
            order.extend(attr for attr in opts['last'] if attr in attrs)
            return order

        def order_attrs(line, orders):
            """Return start tag line, attributes ordered according to orders.

            orders is a dict mapping structure (element) name to a list
            of attribute names.
            """
            struct = ml.element(line)
            attrs = ml.mapping(line)
            default = getarg('default', struct)
            return ml.starttag(struct, ((name, attrs.get(name, default))
                                        for name in orders[struct]))

        # Pass 1: Read input, collecting structural attribute names
        collect_attrs(inf, seekable_inf if write_tmp else None)
        # Pass 2: Read input (original or temporary copy) and write
        # output with attribute names unified and sorted
        if write_tmp:
            with open(seekable_inf_name, 'rb') as seekable_inf:
                unify_attrs(seekable_inf)
        else:
            seekable_inf.seek(0)
            unify_attrs(seekable_inf)
