# -*- mode: Python; -*-

'''Implementation of vrt-add-id.'''

from argparse import ArgumentTypeError
from itertools import count
import math
import random
import re

from libvrt.args import BadData
from libvrt.args import transput_args

from libvrt.metaname import nametype # need checked
from libvrt.metaline import mapping, starttag

# Default maximum random id value (DEFAULT_RAND_END - 1)
DEFAULT_RAND_END = pow(2, 32)

def affix(arg):
    if re.fullmatch('[A-Za-z0-9_\-+/.:]*', arg):
        return arg
    raise ArgumentTypeError('affix out of spec')

def intpow(arg):
    '''argparse argument type check for non-negative integer, 0x... or n^k'''
    if re.fullmatch('[0-9]+|0x[0-9A-Fa-f]+', arg):
        return int(arg, base=0)
    elif re.fullmatch(r'[0-9]+\^[0-9]+', arg):
        base, exp = arg.split('^')
        return pow(int(base), int(exp))
    raise ArgumentTypeError('number out of spec')

def parsearguments(argv, *, prog = None):

    description = '''

    Add or overwrite an "id" attribute to each element of the
    specified kind, based on a counter or unique random values.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--element', metavar = 'name',
                        type = nametype,
                        default = b'sentence',
                        help = '''

                        name of the VRT element to use ("sentence")

                        ''')

    parser.add_argument('--id', dest = 'idn', metavar = 'name',
                        type = nametype,
                        default = b'id',
                        help = '''

                        name of the "id" attribute ("id")

                        ''')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('--counter',
                       action = 'store_const',
                       dest = 'type',
                       const = 'counter',
                       help = '''

                       id values are integers based on a counter (the
                       default)

                        ''')

    group.add_argument('--random',
                       action = 'store_const',
                       dest = 'type',
                       const = 'random',
                       help = '''

                       id values are unique random integers

                       ''')

    parser.add_argument('--seed', metavar = 'string',
                        default = '',
                        help = '''

                        random number generator seed for random ids
                        (default: "" = non-reproducible)

                        ''')

    parser.add_argument('--start', metavar = 'number',
                        type = int,
                        default = 1,
                        help = '''

                        initial value for the counter (1)

                        ''')

    parser.add_argument('--end', metavar = 'number',
                        type = intpow,
                        default = DEFAULT_RAND_END,
                        help = '''

                        maximum random id value is number - 1; a
                        non-negative integer, hexadecimal if prefixed
                        with "0x", or n^k for n to the power of k
                        (default: 2^32)

                        ''')

    parser.add_argument('--prefix', metavar = 'affix',
                        type = affix,
                        default = '',
                        help = '''

                        additional prefix text to each id ("")

                        ''')

    parser.add_argument('--force', action = 'store_true',
                        help = '''

                        overwriting an existing id

                        ''')

    parser.add_argument('--sort', action = 'store_true',
                        help = '''

                        sort element attributes alphabetically
                        (default: keep input order)

                        ''')

    args = parser.parse_args()
    if not args.type:
        args.type = 'counter'
    if not args.seed:
        args.seed = None
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):
    '''Transput VRT (bytes) in ins to VRT (bytes) in ous.'''

    ids = get_idgen(args)

    kind = (b''.join((b'<', args.element, b'>')),
            b''.join((b'<', args.element, b' ')))

    width = get_hexvalue_len(args.end)
    fmt = '{}{:0' + str(width) + 'x}' if args.type == 'random' else '{}{}'

    for line in ins:
        if line.startswith(kind):
            attrs = mapping(line)
            if args.force or args.idn not in attrs:
                attrs[args.idn] = (
                    fmt.format(args.prefix, next(ids)).encode('UTF-8'))
            else:
                raise BadData('element has id already')
            ous.write(starttag(args.element, attrs, sort=args.sort))
        else:
            ous.write(line)

def get_idgen(args):
    '''Return id generator based on args.'''

    if args.type == 'counter':
        # Generator for an integer counter
        return (
            k for k in count(start = args.start)
        )

    else:
        # Multiple generators use different seeds
        if args.seed:
            args.seed += '1'
        return randint_uniq(args.end, args.seed)

def randint_uniq(end, seed=None):
    '''Generator for unique random integers in [0, end[ with seed.'''

    # Values already generated
    used = set()
    rnd = random.Random(seed)
    errmsg = f'more than {end} elements encountered; please increase --end'

    while True:
        if len(used) >= end:
            raise BadData(errmsg)
        r = rnd.randrange(0, end)
        i = 0
        while r in used:
            r = rnd.randrange(0, end)
            i += 1
            # If 1000 consecutive random numbers have already been
            # used, raise an error (1000 is arbitrary)
            if i > 1000:
                raise BadData(errmsg)
        used.add(r)
        yield r

def get_hexvalue_len(value):
    '''Return the number of hex digits required to represent value - 1'''
    return math.ceil(math.log(value) / math.log(16))
