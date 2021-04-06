# -*- mode: Python; -*-

'''Implementation of vrt-add-id.'''

from itertools import count
import re

from libvrt.args import BadData
from libvrt.args import transput_args

from libvrt.metaname import nametype # need checked

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

    parser.add_argument('--force', action = 'store_true',
                        help = '''

                        overwriting an existing id

                        ''')

    args = parser.parse_args()
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):
    '''Transput VRT (bytes) in ins to VRT (bytes) in ous.'''

    ids = (
        str(int(k)).encode('UTF-8')
        for k in count(start = args.start)
    )

    kind = (b''.join((b'<', args.element, b'>')),
            b''.join((b'<', args.element, b' ')))

    for line in ins:
        if line.startswith(kind):
            attrs = dict(re.findall(b'(\S+)="(.*?)"', line))
            if args.force or args.idn not in attrs:
                attrs[args.idn] = next(ids)
            else:
                raise BadData('element has id already')
            ous.write(b'<')
            ous.write(args.element)
            ous.write(b' ')
            ous.write(b' '.join(name + b'="' + value + b'"'
                                for name, value
                                in sorted(attrs.items())))
            ous.write(b'>\n')
        else:
            ous.write(line)
