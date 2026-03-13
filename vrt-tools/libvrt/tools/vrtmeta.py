# -*- mode: Python; -*-

'''Implementation of vrt-meta.'''

import os
from subprocess import Popen, PIPE

from libvrt.args import BadData
from libvrt.args import transput_args

# TODO here AND rel-tools to RAISE not EXIT on failure
from libvrt.bins import SORT

from libvrt.nameargs import bagtype, parsenames
from libvrt.metaline import attributes, valuegetter
from libvrt.metaname import nametype, isname
from libvrt.metamark import marktype

def parsearguments(argv, *, prog = None):

    description = '''

    Present the attribute values of a specified element (default text)
    in a VRT document as a relation in the form of a Tab-Separated
    Values (TSV) document, complete with a head and unique rows in the
    body. (Uniqueness is not guaranteed when using --no-tag.)
    Initially identified attribute names become field names, the
    corresponding values become the content of records. This is not a
    VRT validator.

    '''

    parser = transput_args(description = description,
                           inplace = False)

    parser.add_argument('--quiet', '-q', action = 'store_true',
                        help = '''

                        do not warn when an element has different
                        attributes than the first element (default is
                        to warn four times)

                        ''')

    parser.add_argument('--element', '-e', metavar = 'name',
                        type = nametype,
                        default = b'text',
                        help = '''

                        name of the VRT element to use (defaults to
                        text)

                        ''')

    parser.add_argument('--attr', '-a', metavar = 'name,*',
                        type = bagtype, action = 'append',
                        dest = 'attrs',
                        default = [],
                        help = '''

                        names of attributes to output (repeat, or
                        separate with commas or spaces) (defaults
                        to the attributes in the first element)

                        ''')

    parser.add_argument('--mark', '-m', metavar = 'value',
                        type = marktype,
                        default = b'',
                        help = '''

                        a mark to use as the value for any missing
                        attribute (defaults to the empty string -
                        should the default be visible?)

                        ''')

    group = parser.add_mutually_exclusive_group(required = True)

    group.add_argument('--tag', '-t', metavar = 'name',
                       type = nametype,
                       help = '''

                       name to use for a tag field to number the
                       records of the resulting relation

                       ''')

    group.add_argument('--unique', '-u', action = 'store_true',
                       help = '''

                       omit duplicate records (implies sorting)

                       ''')

    group.add_argument('--no-tag', action = 'store_true',
                       help = '''

                       do not add a tag field nor omit duplicate
                       records (if the output contains duplicates, it
                       is not a relation)

                       ''')

    args = parser.parse_args()
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):
    '''Transput VRT (bytes) in ins to TSV (bytes) in ous.'''

    kind = (b''.join((b'<', args.element, b'>')),
            b''.join((b'<', args.element, b' ')))
    data = (line for line in ins if line.startswith(kind))

    line = next(data, None)
    if line is None:
        raise BadData('no data, no head')

    # attribute names and values in head order,
    # missing attributes default to args.mark
    head = parsenames(args.attrs) or attributes(line)

    if (not all(isname(name) for name in head) or
        len(set(head)) < len(head)):
        raise BadData('bad names (first element)')

    values = valuegetter(head, missing = args.mark,
                         warn = not args.quiet,
                         many = 4,
                         prog = args.prog,
                         # omit "not in head" warnings if attributes
                         # specified explicitly
                         superset = bool(args.attrs))

    if args.tag:
        if args.tag in head:
            raise BadData('tag name in head already')

        def ship(rec, tag):
            ous.write(b'\t'.join((*rec, str(tag).encode('utf-8'))))
            ous.write(b'\n')
            return

        ship(head, args.tag.decode('utf-8'))
        ship(values(line), 1)
        for k, line in enumerate(data, start = 2):
            ship(values(line), k)
        else:
            return 0
    elif args.no_tag:

        def ship(rec):
            ous.write(b'\t'.join(rec))
            ous.write(b'\n')
            return

        ship(head)
        ship(values(line))
        for line in data:
            ship(values(line))
        else:
            return 0
    else:
        # encoded streams seem only available from Python 3.6 on,
        # which is too new, so working in UTF-8 again - maybe that is
        # nicer anyway

        def ship(out, rec):
            out.write(b'\t'.join(rec))
            out.write(b'\n')
            return

        ship(ous, head)
        ous.flush()
        with Popen([ SORT, '--unique' ],
                   env = dict(os.environ,
                              LC_ALL = 'C'),
                   stdin = PIPE,
                   stdout = ous,
                   stderr = None) as proc:
            ship(proc.stdin, values(line))
            for line in data:
                ship(proc.stdin, values(line))
