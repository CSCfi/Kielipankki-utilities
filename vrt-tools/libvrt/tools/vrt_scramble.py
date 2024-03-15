
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
    Scramble the input VRT by randomly shuffling specified structures
    (elements), such as sentences, within containing structures, such
    as texts, and output the scrambled VRT.

    Note that the input may not have intermediate structures between
    the containing structures and the structures to be shuffled; for
    example, if sentences are shuffled within texts, the input may
    not have paragraphs between them.
    """
    ARGSPECS = [
        ('--unit = struct "sentence"',
         '''shuffle struct structures (elements)'''),
        ('--within = struct "text"',
         '''shuffle structures within struct structures (elements):
            structures are not moved across struct boundaries'''),
        ('--seed = string',
         '''use string as the random number generator seed; if string
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
        """Check and modify args (parsed command line arguments)."""
        # Scramble unit and within may not be the same
        if args.within == args.unit:
            self.error_exit(
                'The structure to scramble and the containing structure may'
                ' not be the same')
        if not args.seed:
            # Non-reproducible output
            args.seed = None
        elif args.seed[0] == '<':
            # Read seed from file
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
        """Read inf, write to ouf, with command-line arguments args."""

        def make_starttag_begin(struct):
            """Return (b'<struct ', b'<struct>')."""
            begin = b'<' + struct.encode('UTF-8')
            return (begin + b' ', begin + b'>')

        # If legacy, use random.seed version 1 and the local shuffling
        # method containing a copy of the legacy code
        if args.legacy:
            seed_ver = 1
            self._random_shuffle = self._random_shuffle_legacy
        else:
            seed_ver = 2
            self._random_shuffle = random.shuffle
        random.seed(args.seed, version=seed_ver)
        LT = b'<'[0]
        # Start tag start strings for the within structure
        within_begin = make_starttag_begin(args.within)
        # Start tag start strings for the scramble unit structure
        unit_begin = make_starttag_begin(args.unit)
        # End tag string for the within structure
        within_end = b'</' + args.within.encode('UTF-8') + b'>'
        # End tag string for the scramble unit structure
        unit_end = b'</' + args.unit.encode('UTF-8') + b'>'
        # Whether structures are being collected for scrambling (the
        # current line is inside a within structure)
        collecting = False
        # Scramble units collected in this within structure
        units = []
        # Current scramble unit lines
        current_unit = []
        linenr = 0
        for line in inf:
            linenr += 1
            if collecting:
                if line[0] == LT:
                    if line.startswith(unit_begin):
                        # Add possible current scramble unit to the
                        # collected units and start a new unit
                        if current_unit:
                            units.append(current_unit)
                        current_unit = [line]
                    elif line.startswith(unit_end):
                        # End of scramble unit: add to collected units
                        current_unit.append(line)
                        units.append(current_unit)
                        current_unit = []
                    elif line.startswith(within_end):
                        # Add possible current scramble unit, scramble
                        # the units and output
                        if current_unit:
                            units.append(current_unit)
                        collecting = False
                        for line2 in self._scramble(units):
                            ouf.write(line2)
                        ouf.write(line)
                    elif current_unit == []:
                        # Outside scramble units but within the
                        # structure within which units are scrambled
                        mo = re.match(br'</?([a-z_0-9]+)', line)
                        if mo:
                            # No structure tags allowed here
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
                            # Directly output comment lines after the
                            # start of within
                            ouf.write(line)
                    else:
                        # Structure tag or comment within scramble
                        # unit
                        current_unit.append(line)
                else:
                    # Token line within scramble unit
                    current_unit.append(line)
            else:
                # Outside structures within which to scramble
                # structures
                ouf.write(line)
                if line.startswith(within_begin):
                    # A new within begins
                    units = []
                    current_unit = []
                    collecting = True

    def _scramble(self, units):
        """Randomly shuffle units and yield lines in them."""
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
