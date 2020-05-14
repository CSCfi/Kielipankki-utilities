# -*- mode: Python; -*-

'''Implementation of vrt-name.'''

from argparse import ArgumentTypeError
from itertools import filterfalse, groupby, islice
import re

from libvrt.args import transput_args
from libvrt.bad import BadData

# not to panic - a third of the code below is for deprecated options

def spectype(text):
    if re.fullmatch('(v[1-9][0-9]*=([a-zA-Z_][a-zA-Z0-9_.]*/?)|[, ])*', text):
        return text.encode('UTF-8')
    raise ArgumentTypeError('not "vk=name"*: {}'.format(repr(text)))

def oldspectype(text):
    '''(Deprecated!) extended form of old position-based spec, now
    allowing multiple mappings in each option.

    '''
    if re.fullmatch('([1-9][0-9]*=([a-zA-Z_][a-zA-Z0-9_.]*/?)|[, ])*', text):
        return text.encode('UTF-8')
    raise ArgumentTypeError('not "k=name"*: {}'.format(repr(text)))

def numtype(text):
    '''(Deprecated!)'''
    if re.fullmatch(R'[1-9][0-9]*', text):
        return int(text)
    raise ArgumentTypeError('not a number of fields: {}'.format(repr(text)))

def parsearguments():
    description = '''

    Insert a standard positional-attributes comment at the beginning
    of a VRT document to name the fields. Remove any existing
    positional-attributes comment. Default names are v1, v2 and so.

    '''

    parser = transput_args(description = description)

    group = parser.add_mutually_exclusive_group(required = True)
    
    group.add_argument('--map', '-m', metavar = 'vk=name*',
                       dest = 'mapping', action = 'append',
                       type = spectype, default = [],
                       help = '''

                       map default v1, v2, vk names to desired names,
                       separate by commas or spaces, option can be
                       repeated, greatest vk determines the number of
                       fields

                       ''')

    group.add_argument('--number', '-n', metavar = 'num',
                       type = numtype,
                       help = '''

                       (DEPRECATED) number of fields (instead, -m
                       v3=v3 to specify at least three fields without
                       specifying a name)

                       ''')

    group.add_argument('--position', '-k', metavar = 'k=name*',
                       action = 'append',
                       type = oldspectype, default = [],
                       help = '''

                       (DEPRECATED) name for position k, 1-based
                       (instead, -m v3=ref to name field 3 "ref")

                       ''')

    args = parser.parse_args()
    args.prog = parser.prog
    return args

def isnameline(line):
    return line.startswith(b'<!-- #vrt positional-attributes: ')

def main(args, ins, ous):

    comment = [b'<!-- #vrt positional-attributes:']
    comment.extend(names(args))
    comment.append(b'-->\n')
    length = len(comment) - 2

    ous.write(b' '.join(comment))

    # ignore empty lines
    content = filterfalse(bytes.isspace, ins)

    # sanity-check early tokens lines only
    for line in islice(content, 100):
        if isnameline(line):
            continue
        if line.startswith(b'<'):
            ous.write(line)
            continue
        if line.count(b'\t') + 1 == length:
            ous.write(line)
            continue
        raise BadData('number of fields: expected {}: observed {}'
                      .format(length, line.count(b'\t') + 1))

    # ship the rest without checking
    for kind, group in groupby(content, isnameline):
        if kind: continue
        for line in group: ous.write(line)

    return 0

def names(args):
    '''Turn name options into a (non-empty) list of names.'''

    # deprecated name options --position, --number need supported
    # until removed - must see first if removal is a problem
    if not args.mapping: return deprecatednames(args)

    pairs = [
        pair.split(b'=')
        for pair
        in b' '.join(args.mapping).replace(b',', b' ').split()
    ]

    mapping = dict(pairs)

    if len(mapping) < len(pairs):
        vks = [vk for vk, name in pairs]
        bad = sorted(vk for vk in mapping if vks.count(vk) > 1)
        raise BadData('duplicate vks: {}'
                      .format(b' '.join(bad).decode('UTF-8')))

    high = max((int(old.lstrip(b'v')) for old in mapping),
               default = 0)

    # there is no v0 (by default)
    if not high: raise BadData('no names')

    result = [
        mapping.get(vk, vk)
        for k in range(1, high + 1)
        for vk in ['v{}'.format(k).encode('UTF-8')]
    ]

    res = [name.rstrip(b'/') for name in result]
    if len(set(res)) < len(res):
        bad = sorted(name for name in set(res) if res.count(name) > 1)
        raise BadData('duplicate names: {}'
                      .format(b' '.join(bad).decode('UTF-8')))

    return result

def deprecatednames(args):
    '''Deprecated but need supported until options be removed. Turn
    deprecated options into a (non-empty) list of names'

    '''

    pairs = b' '.join(args.position).replace(b',', b' ').split()
    mapping = dict((b'v' + pos, name)
                   for pos, name
                   in (pair.split(b'=') for pair in pairs))

    if len(mapping) < len(pairs):
        raise BadData('duplicate positions')

    high = max((int(old.lstrip(b'v')) for old in mapping),
               default = int(args.number or 0))

    # there is no v0 (by default)
    if not high: raise BadData('no names')

    return [
        mapping.get(vk, vk)
        for k in range(1, high + 1)
        for vk in ['v{}'.format(k).encode('UTF-8')]
    ]
