
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
         ]),
    ]

    @staticmethod
    def encode_utf8(s):
        """Argument type function converting str s to UTF-8 bytes."""
        return s.encode('UTF-8')

    @staticmethod
    def attrlist(s):
        """Argument type function for a list of unique attribute names.

        The attributes in str s can be separated by commas or spaces.
        Return a list of bytes.

        If the attribute list contains duplicates, raise
        ArgumentTypeError.
        """
        attrs = re.split(r'[,\s]+', s or '')
        dupls = _find_duplicates(attrs)
        if dupls:
            raise ArgumentTypeError(
                'duplicate attribute names: ' + ', '.join(dupls))
        return [attr.encode('UTF-8') for attr in attrs]

    def __init__(self):
        # extra_types=... is needed for using the above static methods
        # as the type in ARGSPECS (otherwise, type could be passed via
        # a dict)
        super().__init__(extra_types=self.__class__.__dict__)

    def check_args(self, args):
        """Check and modify args (parsed command line arguments)."""

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

        check_first_last_dupls(args)
        for struct, struct_args in args.structure.items():
            check_first_last_dupls(struct_args, struct)

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
            order = make_order()
            for line in inf:
                if ml.ismeta(line) and ml.isstarttag(line):
                    line = order_attrs(line, order)
                ouf.write(line)

        def make_order():
            """Return dict[list] containing attr order for each struct."""
            order = {}
            for struct, attrs in struct_attrs.items():
                input_order = getarg('input_order', struct)
                first = getarg('first', struct)
                last = getarg('last', struct)
                sortfn = (lambda x: x) if input_order else sorted
                attrs = sortfn(list(attrs.keys()))
                order[struct] = [attr for attr in first if attr in attrs]
                order[struct].extend(attr for attr in attrs
                                     if attr not in first and attr not in last)
                order[struct].extend(attr for attr in last if attr in attrs)
            return order

        def order_attrs(line, order):
            """Return start tag line, attributes ordered according to order.

            order is a dict mapping structure (element) name to a list
            of attribute names.
            """
            struct = ml.element(line)
            attrs = ml.mapping(line)
            default = getarg('default', struct)
            return ml.starttag(struct, ((name, attrs.get(name, default))
                                        for name in order[struct]))

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
