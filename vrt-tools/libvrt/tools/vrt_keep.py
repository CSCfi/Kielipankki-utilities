# -*- mode: Python; -*-

'''Implement vrt-keep.

Warning! Any '+' in field names is no longer expected. Develop a
transparent mechanism to deal with internal structure instead.

'''

from itertools import chain, filterfalse, islice
import enum, os, re, sys, traceback


from libvrt.args import transput_args
from libvrt.bad import BadData, BadCode
from libvrt.keeper import keeper
from libvrt.nameargs import bagtype, parsenames
from libvrt.nameline import isnameline, parsenameline, makenameline

def parsearguments():
    description = '''

    Keep the fields (positional attributes) named in the options.
    Also keep them in that order, with any --rest fields in their
    order in the input.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--field', '-f', metavar = 'name,*',
                        dest = 'fields', default = [],
                        type = bagtype, action = 'append',
                        help = '''

                        fields to keep, separate names by commas or
                        spaces, or repeat the option

                        ''')

    parser.add_argument('--names', '-n', metavar = 'name,*',
                        dest = 'fields', action = 'append',
                        type = bagtype, default = [],
                        help = '(deprecated) use --field/-f instead')

    # cannot seem to enforce at most one --rest, nargs gives error, so
    # check afterwards that there was at most one
    parser.add_argument('--rest', const = b'[...]',
                        dest = 'fields', action = 'append_const', 
                        help = '''

                        keep the remaining fields

                        ''')

    args = parser.parse_args()
    args.prog = parser.prog
    return args


def getget(args, source):
    '''From args.names from the command line and field names given in
    data, return a getter of the desired fields. (Always also include
    the pseudo-name '+' if the document is made "flat" and contains
    it, but never in the first position because that field may contain
    bare angles.)

    '''

    index = { name : k for k, name in enumerate(source) }

    # hit https://bugs.python.org/issue4806 (totally confusing error
    # message) when --rest stored a string (should have appended a
    # bytes object, so a double bug but anyway) to args.names; second
    # time hitting a bug in Python 3.4 that is fixed in Python 3.5
    target = list(chain(*(names.split(b',') for names in args.names)))

    what = [ name for name in target
             if name != b'[...]'
             if name not in index ]
    if what:
        raise BadData('no such name: ' + what[0].decode('UTF-8'))

    unique = set(target)
    if len(unique) < len(target):
        raise BadData('duplicates')

    if b'[...]' in unique:
        rest = target.index(b'[...]')
        target[rest:rest + 1] = (name for name in source
                                 if name not in unique)

    if not target:
        raise BadData('empty target')

    # target can contain '+' but cannot start with '+' (assuming input
    # is valid) because '+' is not valid in options, so either a
    # proper first field name is given, or --rest picks an actual
    # first field which again cannot be '+' field

    # include any '+' even without --rest option
    if b'+' in index and b'+' not in target: target.append(b'+')

    positions = (index[name] for name in target)
    if len(target) == 1:
        getone = itemgetter(*positions)
        getter = lambda record: (getone(record),)
    else:
        getter = itemgetter(*positions)

    return getter

def main(args, ins, ous):

    if args.fields.count(b'[...]') > 1:
        raise BadData('more than one --rest')

    if b'[...]' in args.fields:
        rest = args.fields.index(b'[...]')
        before = parsenames(args.fields[:rest])
        after = parsenames(args.fields[rest + 1:])
    else:
        before = parsenames(args.fields)
        after = parsenames([])

    content = filterfalse(bytes.isspace, ins)

    head = islice(content, 100)
    for line in head:
        if isnameline(line):
            names = parsenameline(line, required = before + after)
            between = ( [ name for name in names # oh slash TODO
                          if name not in before
                          if name not in after ]
                        if b'[...]' in args.fields
                        else []
            )
            # print(names, '=>', before, between, after)
            ix = tuple(names.index(name) for name
                       in before + between + after)
            if not ix:
                raise BadData('must keep some of the fields: {}'
                              .format(b' '.join(names).decode('UTF-8')))
            keep = keeper(*ix)
            ous.write(makenameline(keep(names)))
            break
        elif line.startswith(b'<'):
            ous.write(line)
        else:
            raise BadData('field found before field names')
    else:
        raise BadData('first 100 lines: no field names found')

    # broke out of head so found and shipped a name line
    for line in filterfalse(isnameline, chain(head, content)):
        if line.startswith(b'<'):
            ous.write(line)
            continue

        ous.write(b'\t'.join(keep(line.rstrip(b'\r\n').split(b'\t'))))
        ous.write(b'\n')

    return 0
