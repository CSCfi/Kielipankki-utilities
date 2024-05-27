
"""
vrt_unify_attrs.py

The actual implementation of vrt-unify-attrs.

Please run "vrt-unify-attrs -h" for more information.
"""


import sys
import re

from collections import defaultdict, OrderedDict
from tempfile import NamedTemporaryFile

from libvrt import metaline as ml

from vrtargsoolib import InputProcessor


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
        ('--default = str ""',
         '''add missing attributes with value str'''),
        ('--input-order',
         '''order attributes to the order first encountered in input,
            instead of sorting alphabetically; attributes encountered
            only later are appended'''),
    ]

    def __init__(self):
        super().__init__()

    def check_args(self, args):
        """Check and modify args (parsed command line arguments)."""
        args.default = args.default.encode('UTF-8')

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
            sortfn = (lambda x: x) if args.input_order else sorted
            return dict((struct, sortfn(list(attrs.keys())))
                        for struct, attrs in struct_attrs.items())

        def order_attrs(line, order):
            """Return start tag line, attributes ordered according to order.

            order is a dict mapping structure (element) name to a list
            of attribute names.
            """
            struct = ml.element(line)
            attrs = ml.mapping(line)
            return ml.starttag(struct, ((name, attrs.get(name, args.default))
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
