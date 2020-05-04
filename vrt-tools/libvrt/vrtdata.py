# -*- mode: Python; -*-

'''Implementation of vrt-data.'''

import os
from subprocess import Popen, PIPE

from .args import BadData
from .args import transput_args

# TODO here AND rel-tools to RAISE not EXIT on failure
from .bins import SORT

from .dataline import valuegetter

# remnants of vrt-meta seem good here
from .metaname import nametype, isname
from .metamark import marktype

def parsearguments(argv, *, prog = None):

    description = '''

    Present the annotated tokens in a VRT document as a relation in
    the form of a Tab-Separated Values (TSV) document, complete with a
    head and unique rows in the body. Initially identified positional
    names become field names, or default to v1, v2, up to the
    initially encountered number of fields, while the corresponding
    values become the content of records. This is not a VRT validator.

    '''

    parser = transput_args(description = description,
                           inplace = False)

    parser.add_argument('--quiet', '-q', action = 'store_true',
                        help = '''

                        do not warn when a token has a different
                        number of annotations than the first name
                        comment or the first token (default is to warn
                        four times)

                        ''')

    parser.add_argument('--mark', '-m', metavar = 'value',
                        type = marktype,
                        default = b'',
                        help = '''

                        a mark to use as the value when there are too
                        few fields (defaults to the empty string -
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

    args = parser.parse_args()
    args.prog = prog or parser.prog

    # ==============================================
    # TODO make *transput* work *without* these !!!! ALREADY
    # ==============================================
    args.inplace = None
    args.backup = None

    return args

def main(args, ins, ous):
    '''Transput VRT (bytes) in ins to TSV (bytes) in ous.'''

    data = (
        line for line in ins
        if not line.isspace()
        if (
                not (line.startswith(b'<')) or
                line.startswith(b'<!-- #vrt positional attributes: ')
        )
    )

    line = next(data, None)
    if line is None:
        raise BadData('no data, no head')

    if line.startswith(b'<'):
        left, rest = line.rstrip(b'->\r\n').split(b':')
        head = rest.split()
    else:
        head = [
            'v{}'.format(k).encode('utf-8')
            for k, v
            in enumerate(line.rstrip(b'\r\n').split(b'\t'),
                         start = 1)
        ]

    if (not all(isname(name) for name in head) or
        len(set(head)) < len(head)):
        raise BadData('bad names')

    values = valuegetter(head, missing = args.mark,
                         warn = not args.quiet,
                         many = 4,
                         prog = args.prog)

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
