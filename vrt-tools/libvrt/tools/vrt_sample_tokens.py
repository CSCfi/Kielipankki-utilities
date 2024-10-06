import random # to use random.seed

from itertools import chain, islice

from libvrt.args import transput_args
from libvrt.metaname import nametype # need checked
from libvrt.nameline import isnameline
from libvrt.reservoir import sample_iter

def parsearguments(argv, *, prog = None):

    description = '''

    Sample a desired number of tokens from a VRT source, uniformly
    over all occurrences, using a reservoir method. Only the sample
    needs to fit in memory.

    '''

    parser = transput_args(description = description,
                           inplace = False)

    parser.add_argument('--number', '-n', metavar = 'n',
                        required = True,
                        type = int, # do we have nat or "pos" somewhere
                        # guess there is no sensible default to put here
                        help = '''

                        the number of elements in the sample (all of
                        them if there are fewer of them)

                        ''')

    parser.add_argument('--seed',
                        help = '''

                        any string whatsoever, hoping to get a
                        repeatable run of random numbers in return

                        ''')

    parser.add_argument('--wrap', metavar = 'name',
                        type = nametype,
                        help = '''

                        wrap the whole sample in this element, to have
                        all tokens inside an element; a suggested name
                        might be "sample"

                        ''')

    args = parser.parse_args()
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):
    '''Transput VRT (bytes) in ins to VRT (bytes) in ous.'''

    # using the same string as the seed may or may not produce a
    # repeatable random sequence across machines and pythons; the
    # intention is that it would but who really knows; the sampler
    # uses Python's random module and does not take a generator as an
    # argument, so this is as far as one cares to bother for now
    random.seed(args.seed)

    # for this tool, do not even require positional-attributes line
    # but quietly preserve the line if found in the first 100 lines
    head = tuple(islice(ins, 100))
    for line in head:
        if isnameline(line):
            ous.write(line)
            break

    if args.wrap is not None:
        ous.write(b'<' + args.wrap + b'>\n')

    population = ( line for line in chain(head, ins)
                   if not line.startswith(b'<')
                   if not line.isspace()
    )

    # the enumeration provides the means to put the final pool back in
    # the input order, otherwise they would appear in a random order
    pool = sample_iter(enumerate(population), args.number)

    pool.sort()

    for k, line in pool:
        ous.write(line)

    if args.wrap is not None:
        ous.write(b'</' + args.wrap + b'>\n')

