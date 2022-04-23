# -*- mode: Python; -*-

'''Support the parsing of any command line options that pertain to
field names.

'''

from argparse import ArgumentTypeError
import re

from libvrt.bad import BadData

def nametype(arg):
    '''Approximately safe to use as a field name.'''
    if re.fullmatch('\w+', arg, re.ASCII):
        return arg.encode('UTF-8')
    raise ArgumentTypeError('bad name: ' + repr(arg))

def prefixtype(arg):
    '''Approximately safe to use as a prefix to a field name.'''
    if re.fullmatch('\w*', arg, re.ASCII):
        return arg.encode('UTF-8')
    raise ArgumentTypeError('bad prefix: ' + repr(arg))

def suffixtype(arg):
    '''Approximately safe to use as a suffix to a field name.'''
    if re.fullmatch('\w*', arg, re.ASCII):
        return arg.encode('UTF-8')
    raise ArgumentTypeError('bad suffix: ' + repr(arg))

def maptype(text):
    if re.fullmatch('([a-zA-Z_][a-zA-Z0-9_.]*/?'
                    '=[a-zA-Z_][a-zA-Z0-9_.]*/?'
                    '|[, ])*',
                    text):
        return text.encode('UTF-8')
    raise ArgumentTypeError('not name mappings: {}'
                            .format(repr(text)))

def bagtype(text):
    if re.fullmatch('([a-zA-Z_][a-zA-Z0-9_.]*/?|[, ])*', text):
        return text.encode('UTF-8')
    raise ArgumentTypeError('not field names: {}'.format(repr(text)))

def parsemaps(option, *, default = False):
    '''Parse an option value that specifies mappings from old field names
    to new field names. The argument is a list of byte strings that
    consist of any number of pairs in the form b'old=new' separated by
    any number commas or spaces (or both). If default is True, every
    "old" must be of the form "vk" where "k" is the canonical written
    representation of a positive integer.

    An empty mapping is allowed. Duplicate "old" are not allowed.

    Return the mapping as a dict, or raise a BadData exception.

    Used by vrt-name (default) and vrt-rename.

    '''
    pairs = [
        pair.split(b'=')
        for pair
        in b' '.join(option).replace(b',', b' ').split()
    ]

    mapping = dict(pairs)

    # disallow multiple mappings
    if len(mapping) < len(pairs):
        old = [ key for key, val in pairs ]
        bad = [ key for key in mapping if old.count(key) > 1 ]
        raise BadData('mapped more than once: {}'
                      .format(b' '.join(bad).decode('UTF-8')))

    return mapping

def parsenames(option):
    '''Parse an option value that specifies field names. The argument is a
    list of byte strings that consist of any number of field names
    separated by any number of commas or spaces (or both).

    An empty list is allowed. Duplicates are not allowed.

    Used in vrt-keep and vrt-drop.

    '''
    names = b' '.join(option).replace(b',', b' ').split()

    if len(set(names)) < len(names):
        bad = sorted(set(name for name in names if names.count(name) > 1))
        raise BadData('named more than once: {}'
                      .format(b' '.join(bad).decode('UTF-8')))

    return names
