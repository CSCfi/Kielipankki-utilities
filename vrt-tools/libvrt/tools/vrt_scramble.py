
"""
vrt_scramble.py

The actual implementation of vrt-scramble.

Please run "vrt-scramble -h" for more information.
"""


import sys
import re
import random

from math import floor

from vrtargsoolib import InputProcessor


class VrtScrambler(InputProcessor):

    """Class implementing vrt-scramble functionality."""

    DESCRIPTION = """
    Scramble (randomly shuffle) given structures (elements), such as
    sentences, within larger structures, such as texts, in the VRT
    input and output the scrambled VRT.

    Note that the input may not have intermediate structures between
    the containing structures and the structures to be scrambled; for
    example, if sentences are scrambled within texts, the input may
    not have paragraphs.
    """
    ARGSPECS = [
        ('--unit = struct "sentence"',
         '''shuffle struct structures (elements)'''),
        ('--within = struct "text"',
         '''shuffle structures within struct structures (elements):
            structures are not moved across struct boundaries'''),
        ('--seed = string',
         '''set random number generator seed to string; if string
            begins with "<", the rest is the name of the file whose
            content (up to 1 MiB) to use as the seed (default: "" =
            non-reproducible output)''',
         dict(default='')),
        ('--legacy',
         '''produce the same result as the old vrt-scramble.py for any
            non-empty seed'''),
    ]

    # Maximum number of bytes to read from a random seed file
    MAX_SEED_BYTES = pow(2, 20)

    def __init__(self):
        super().__init__()

    def check_args(self, args):
        if not args.seed:
            args.seed = None
        elif args.seed[0] == '<':
            args.seed = self._read_file_content(args.seed[1:].strip(),
                                                self.MAX_SEED_BYTES)

    def _read_file_content(self, filename, max_bytes):
        """Return up to max_bytes bytes from the beginning of file filename.

        An IOError when trying to read the file causes the program to
        terminate with an error message and exit code 1.
        """
        try:
            with open(filename, 'rb') as f:
                return f.read(max_bytes)
        except IOError as e:
            self.error_exit(
                f'Cannot read random seed from file {filename}: {e}')
        # Should never get here
        return None

    def main(self, args, inf, ouf):

        def make_starttag_begin(struct):
            begin = b'<' + struct.encode('UTF-8')
            return (begin + b' ', begin + b'>')

        if args.legacy:
            seed_ver = 1
            self._random_shuffle = self._random_shuffle_legacy
        else:
            seed_ver = 2
            self._random_shuffle = random.shuffle
        random.seed(args.seed, version=seed_ver)
        LT = b'<'[0]
        within_begin = make_starttag_begin(args.within)
        unit_begin = make_starttag_begin(args.unit)
        within_end = b'</' + args.within.encode('UTF-8') + b'>'
        unit_end = b'</' + args.unit.encode('UTF-8') + b'>'
        collecting = False
        units = []
        current_unit = []
        linenr = 0
        for line in inf:
            linenr += 1
            if collecting:
                if line[0] == LT:
                    if line.startswith(unit_begin):
                        if current_unit:
                            units.append(current_unit)
                        current_unit = [line]
                    elif line.startswith(unit_end):
                        # End of scramble unit: add to collected units
                        current_unit.append(line)
                        units.append(current_unit)
                        current_unit = []
                    elif line.startswith(within_end):
                        if current_unit:
                            units.append(current_unit)
                        collecting = False
                        for line2 in self._scramble(units):
                            ouf.write(line2)
                        ouf.write(line)
                    elif current_unit == []:
                        mo = re.match(br'<([a-z_0-9]+)', line)
                        if mo:
                            struct = mo.group(1)
                            self.error_exit(
                                'Structure \'' + struct.decode('UTF-8')
                                + f'\' between \'{args.within}\' and'
                                + f' \'{args.unit}\'',
                                filename=inf.name, linenr=linenr)
                        elif units:
                            # Append comment lines following the end
                            # tag of a unit structure to the preceding
                            # unit
                            units[-1].append(line)
                        else:
                            # Output comment lines directly after the
                            # start of within
                            ouf.write(line)
                    else:
                        current_unit.append(line)
                else:
                    current_unit.append(line)
            else:
                ouf.write(line)
                if line.startswith(within_begin):
                    units = []
                    current_unit = []
                    collecting = True

    def _scramble(self, units):
        self._random_shuffle(units)
        for unit in units:
            for line in unit:
                yield line

    def _random_shuffle_legacy(self, seq):
        """Randomly shuffle seq, same results as Python 2 random.shuffle."""
        # This code was copied from the Python 3.10 library code for
        # random.shuffle. Up to Python 3.10, the same result could be
        # achieved by using random.shuffle(seq, random=random.random),
        # but the parameter random will be removed in Python 3.11
        # (deprecated in 3.9).
        for i in reversed(range(1, len(seq))):
            # pick an element in seq[:i+1] with which to exchange seq[i]
            j = floor(random.random() * (i + 1))
            seq[i], seq[j] = seq[j], seq[i]
