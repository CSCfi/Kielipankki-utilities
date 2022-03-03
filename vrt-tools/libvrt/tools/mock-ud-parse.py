'''This is a mock parser for simplest ConLLU (UD2), for developing VRT
parsers that use real UD2 parsers. Standard input is assumed to be
ten-field tab-separated records in groups separated by empty
lines. Standard output is the same, ID and FORM fields echoed and
other fields filled in a silly way.

https://universaldependencies.org/format.html

'''

from itertools import groupby
from sys import stdin, stdout

def main(ins, ous):
    for kind, group in groupby(ins, bytes.isspace):
        if not kind:
            for line in group:
                [
                    ID,
                    FORM, LEMMA,
                    UPOS, XPOS, FEATS,
                    HEAD, DEPREL,
                    DEPS, MISC
                ] = line.rstrip(b'\r\n').split(b'\t')
                ous.write(b'\t'.join((
                    ID,
                    FORM, b'=' + FORM,
                    b'X', b'_', b'_',
                    b'0', b'dep',
                    b'_', b'Type=Mock'
                )))
                ous.write(b'\n')
            else:
                ous.write(b'\n')

if __name__ == '__main__':
    main(stdin.buffer, stdout.buffer)
