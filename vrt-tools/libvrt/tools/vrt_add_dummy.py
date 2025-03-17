
"""
vrt_add_dummy.py

The actual implementation of vrt-add-dummy.

Please run "vrt-add-dummy -h" for more information.
"""


# TODO:
# - Polish code
# - Add tests
# - Specify attributes for intermediate structures
# - Handle non-nested structures such as pages


import re

import vrtargsoolib
from libvrt import nameline
from libvrt import metaline
from libvrt.argtypes import attr_value, encode_utf8
from libvrt.args import BadData


class VrtDummyTokenAdder(vrtargsoolib.InputProcessor):

    """Class implementing vrt-add-dummy functionality."""

    DESCRIPTION = """
    Add a dummy token to empty structures (elements) (texts,
    paragraph, sentences) in the input VRT. If an empty text has no
    sentence and paragraph structures, also add them.
    """
    ARGSPECS = [
        ('--attribute-value = attr:attr_value -> attr_values',
         """Positional attribute attr of a dummy token has value.""",
         dict(action='append',
              metavar='attr=value')),
        ('--default = value:encode_utf8 "_" -> default_value',
         """Positional attributes of a dummy token have value unless
            otherwise specified with --attribute-value."""),
        ('--empty-attribute = attrname:encode_utf8 "empty" -> empty_attr',
         """Add to texts attribute attrname with value "y" in empty
            texts and "n" in non-empty ones"""),
        ('--intermediate = structlist -> intermed_structs',
         """Add structures listed in structlist between text and
            sentence to an empty text without sentences (typically
            paragraph)."""),
    ]
        
    def __init__(self):
        # extra_types=... is needed for using module-level functions
        # as types in ARGSPECS (otherwise, type could be passed via a
        # dict)
        super().__init__(extra_types=globals())

    def check_args(self, args):
        """Check and modify args (parsed command line arguments)."""
        args.attr_values = dict(args.attr_values or [])
        args.intermed_structs = [
            struct.encode('utf-8')
            for struct in re.split('[, ]+', args.intermed_structs or '')]
        if args.intermed_structs == [b'']:
            args.intermed_structs = []

    def main(self, args, inf, ouf):
        """Read inf, write to ouf, with command-line arguments args."""

        def make_empty_token_line(posattrs):
            return b'\t'.join(args.attr_values.get(posattr, args.default_value)
                              for posattr in posattrs) + b'\n'

        def add_empty_attr(line, isempty):
            return (line.rstrip(b'>\n')
                    + b' ' + args.empty_attr + b'="'
                    + (b'y' if isempty else b'n')
                    + b'">\n')

        def make_dummy(struct_stack):
            if posattrs is None:
                raise BadData(
                    'No positional-attributes comment before the first token')
            add_lines = []
            for struct in args.intermed_structs:
                add_lines.append(metaline.starttag(struct, ()))
            add_lines.append(empty_token_line)
            for struct in reversed(args.intermed_structs):
                add_lines.append(b'</' + struct + b'>\n')
            return add_lines

        LESS_THAN = b'<'[0]
        posattrs = None
        empty_token_line = None
        struct_stack = []
        write_queue = []
        text_begin = None
        isempty = True
        for line in inf:
            if line[0] == LESS_THAN:
                if metaline.isstarttag(line):
                    struct = metaline.element(line)
                    if struct == b'text':
                        text_begin = len(write_queue)
                    struct_stack.append(struct)
                    write_queue.append(line)
                    isempty = True
                elif metaline.isendtag(line):
                    struct = metaline.element(line)
                    struct_stack.pop()
                    if write_queue:
                        write_queue[text_begin] = add_empty_attr(
                            write_queue[text_begin], isempty)
                        ouf.writelines(write_queue)
                        write_queue = []
                        if isempty:
                            ouf.writelines(make_dummy(struct_stack))
                    ouf.write(line)
                elif nameline.isnameline(line):
                    posattrs = nameline.parsenameline(line)
                    empty_token_line = make_empty_token_line(posattrs)
                    ouf.write(line)
            else:
                isempty = False
                if posattrs is None:
                    raise BadData(
                        'No positional-attributes comment before the first token')
                if write_queue:
                    write_queue[text_begin] = add_empty_attr(
                            write_queue[text_begin], isempty)
                    ouf.writelines(write_queue)
                    write_queue = []
                ouf.write(line)
