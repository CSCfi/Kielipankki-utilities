
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
    not have paragraphs between texts and sentences.
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
        # Shuffle unit and within structures may not be the same
        if args.within == args.unit:
            self.error_exit(
                'The structure to shuffle and the containing structure may'
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

        def make_tag_prefixes(struct):
            """Return start and end tag prefixes (bytes) for struct."""
            struct_b = struct.encode('UTF-8')
            return ((b'<' + struct_b + b' ', b'<' + struct_b + b'>'),
                    b'</' + struct_b + b'>')

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
        # Start and end tag prefixes for container structure
        container_start, container_end = make_tag_prefixes(args.within)
        # Start and end tag prefixes for shuffle item structure
        item_start, item_end = make_tag_prefixes(args.unit)
        # Whether structures are being collected for shuffling (the
        # current line is inside a container structure)
        collecting = False
        # Shuffle items collected in this container structure
        items = []
        # Current shuffle item lines
        current_item = []
        linenr = 0
        for line in inf:
            linenr += 1
            if collecting:
                if line[0] == LT:
                    if line.startswith(item_start):
                        # Add possible current shuffle item to the
                        # collected items and start a new item
                        if current_item:
                            items.append(current_item)
                        current_item = [line]
                    elif line.startswith(item_end):
                        # End of shuffle item: add to collected items
                        current_item.append(line)
                        items.append(current_item)
                        current_item = []
                    elif line.startswith(container_end):
                        # Add possible current shuffle item, shuffle
                        # the items and output
                        if current_item:
                            items.append(current_item)
                        collecting = False
                        for line2 in self._shuffle(items):
                            ouf.write(line2)
                        ouf.write(line)
                    elif current_item == []:
                        # Outside shuffle items but within container
                        mo = re.match(br'</?([a-z_0-9]+)', line)
                        if mo:
                            # No structure tags allowed here
                            struct = mo.group(1)
                            self.error_exit(
                                f"Structure '{struct.decode('UTF-8')}' not"
                                f" allowed between container '{args.within}'"
                                f" and shuffle item '{args.unit}'",
                                filename=inf.name, linenr=linenr)
                        elif items:
                            # Append comment lines following the end
                            # tag of an item to the preceding item
                            items[-1].append(line)
                        else:
                            # Directly output comment lines after the
                            # start of a container
                            ouf.write(line)
                    else:
                        # Structure tag or comment within shuffle item
                        current_item.append(line)
                else:
                    # Token line within shuffle item
                    current_item.append(line)
            else:
                # Outside container structures
                ouf.write(line)
                if line.startswith(container_start):
                    # A new container begins
                    items = []
                    current_item = []
                    collecting = True

    def _shuffle(self, items):
        """Randomly shuffle items and yield lines in them."""
        self._random_shuffle(items)
        for item in items:
            for line in item:
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
