#! /usr/bin/env python3


import os.path
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../../vrt-tools')))
import vrtargsoolib


class DummyContentAdder(vrtargsoolib.InputProcessor):

    DESCRIPTION = """
    Replace completely empty messages (empty text structures) in VRT
    with a dummy text in a sentence and paragraph.
    """

    def __init__(self):
        super().__init__()

    def main(self, args, inf, ouf):
        dummy_content = """<paragraph type="empty_message">
<sentence>
_\t_\tPunct\t_\t1\t0\tROOT\t_\t1
</sentence>
</paragraph>
""".encode()

        def output_lines(lines):
            for line in lines:
                ouf.write(line)

        def make_dummy(text):
            # Assume \n line terminator and no trailing whitespace
            text[0] = text[0][:-2] + b' empty_message="true"' + text[0][-2:]
            text[1:1] = [dummy_content]
            return text

        text = []
        for line in inf:
            text.append(line)
            if line.startswith(b'</text>'):
                if (len(text) == 2):
                    output_lines(make_dummy(text))
                else:
                    output_lines(text)
                text = []


if __name__ == '__main__':
    DummyContentAdder().run()
