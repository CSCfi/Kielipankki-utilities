#! /usr/bin/env python3


import os.path
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../../vrt-tools')))
import vrtargsoolib


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
        dummy_content = """<paragraph type="empty">
<sentence>
_\t_\tPunct\t_\t1\t0\tROOT\t_\t1
</sentence>
</paragraph>
""".encode()
        empty_attr = {
            True: b' empty="y"',
            False: b' empty="n"',
        }

        def output_lines(lines):
            for line in lines:
                ouf.write(line)

        def add_empty_attr(line, empty):
            # Assume \n line terminator and no trailing whitespace
            return line[:-2] + empty_attr[empty] + line[-2:]

        def make_dummy(text):
            text[0] = add_empty_attr(text[0], True)
            text[1:1] = [dummy_content]
            return text

        def make_nonempty(text):
            text[0] = add_empty_attr(text[0], False)
            return text

        text = []
        for line in inf:
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
