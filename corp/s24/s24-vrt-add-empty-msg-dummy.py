#! /usr/bin/env python3


# TODO:
# - Make the script more general (not specific to Suomi24) by adding options
#   for specifying names for the empty attributes and their values and
#   whether a paragraph level should be added.
# - Rename and move to vrt-tools.


import os.path
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../../vrt-tools')))
import vrtargsoolib
import vrtnamelib


class DummyContentAdder(vrtargsoolib.InputProcessor):

    DESCRIPTION = """
    Replace completely empty messages (empty text structures) in VRT
    with a dummy text in a sentence and paragraph (with type="empty").
    Add attribute empty="y" to empty text structures and empty="n" to
    non-empty ones.
    """

    def __init__(self):
        super().__init__()

    def main(self, args, inf, ouf):
        dummy_posattrs = dict(
            DEFAULT='_',
            pos='Punct',
            ref='1',
            dephead='0',
            deprel='ROOT',
            initid='1',
            wid='1',
        )
        # FIXME: This does not produce the correct result if the number or
        # order of attributes is different. Or should we simply require the
        # positional-attributes comment?
        default_posattrs = (
            b'word lemma pos msd ref dephead deprel spaces initid'.split())
        dummy_container = """<paragraph type="empty">
<sentence>
{line}
</sentence>
</paragraph>
"""
        dummy_content = None
        default_dummy_content = None
        empty_attr = {
            True: b' empty="y"',
            False: b' empty="n"',
        }

        def create_dummy(posattrs):
            token_line = '\t'.join(
                dummy_posattrs.get(attr.decode(), dummy_posattrs['DEFAULT'])
                for attr in posattrs)
            return dummy_container.format(line=token_line).encode()

        def output_lines(lines):
            for line in lines:
                ouf.write(line)

        def add_empty_attr(line, empty):
            # Assume \n line terminator and no trailing whitespace
            return line[:-2] + empty_attr[empty] + line[-2:]

        def make_dummy(text):
            text[0] = add_empty_attr(text[0], True)
            text[1:1] = [dummy_content or default_dummy_content]
            return text

        def make_nonempty(text):
            text[0] = add_empty_attr(text[0], False)
            return text

        default_dummy_content = create_dummy(default_posattrs)
        text = []
        for line in inf:
            if not (text or (line.startswith(b'<text') and line[5] in b' >')):
                # Outside <text>, for example a VRT comment
                if not dummy_content and vrtnamelib.isbinnames(line):
                    dummy_content = create_dummy(vrtnamelib.binnamelist(line))
                ouf.write(line)
            else:
                text.append(line)
                if line.startswith(b'</text>'):
                    if (len(text) == 2):
                        text = make_dummy(text)
                    else:
                        text = make_nonempty(text)
                    output_lines(text)
                    text = []


if __name__ == '__main__':
    DummyContentAdder().run()
