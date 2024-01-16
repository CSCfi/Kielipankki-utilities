# -*- mode: Python; -*-

'''Implementation of vrt-add-id.'''

from argparse import ArgumentTypeError
from itertools import count
import re

from libvrt.args import BadData
from libvrt.args import transput_args

from libvrt.metaname import nametype # need checked
from libvrt.metaline import mapping, starttag

def affix(arg):
    if re.fullmatch('[A-Za-z0-9_\-+/.:]*', arg):
        return arg
    raise ArgumentTypeError('affix out of spec')

def parsearguments(argv, *, prog = None):

    description = '''

    Add or overwrite an "id" attribute to each element of the
    specified kind, based on a counter.

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

    parser.add_argument('--start', metavar = 'number',
                        type = int,
                        default = 1,
                        help = '''

                        initial value for the counter (1)

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
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):
    '''Transput VRT (bytes) in ins to VRT (bytes) in ous.'''

    ids = (
        '{}{}'.format(args.prefix, k).encode('UTF-8')
        for k in count(start = args.start)
    )

    kind = (b''.join((b'<', args.element, b'>')),
            b''.join((b'<', args.element, b' ')))

    for line in ins:
        if line.startswith(kind):
            attrs = mapping(line)
            if args.force or args.idn not in attrs:
                attrs[args.idn] = next(ids)
            else:
                raise BadData('element has id already')
            ous.write(starttag(args.element, attrs, sort=args.sort))
        else:
            ous.write(line)
