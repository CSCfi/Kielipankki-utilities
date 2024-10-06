import random # to use random.seed

from itertools import chain, islice

from libvrt.args import transput_args
from libvrt.elements import elements
from libvrt.metaname import nametype # need checked
from libvrt.nameline import isnameline
from libvrt.reservoir import sample_iter

def parsearguments(argv, *, prog = None):

    description = '''

    Sample a desired number of elements from a VRT source, uniformly
    over all occurrences, using a reservoir method. Only the sample
    needs to fit in memory. (Be warned that there is no checking for
    possible begins or ends of overlapping structural annotations.
    Any such will be left dangling in the output.)

    '''

    parser = transput_args(description = description,
                           inplace = False)

    parser.add_argument('--element', '-e', metavar = 'name',
                        type = nametype,
                        default = b'sentence',
                        help = '''

                        name of the element to sample ("sentence")

                        ''')

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

    # the reification of all eligible elements is because we are not
    # sufficiently smart to reify only those elements that end in the
    # pool ever at all, let alone those that remain the in final pool
    # (the ous=None discards all material outside the element type)
    source = chain(head, ins)
    population = map(tuple, elements(args.element, source, ous=None))

    # the enumeration provides the means to put the final pool back in
    # the input order, otherwise they would appear in a random order
    pool = sample_iter(enumerate(population), args.number)

    pool.sort()

    for k, lines in pool:
        for line in lines:
            ous.write(line)
