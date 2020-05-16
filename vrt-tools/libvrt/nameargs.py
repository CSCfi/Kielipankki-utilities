# -*- mode: Python; -*-

'''Support the parsing of any command line options that pertain to
field names.

'''

from argparse import ArgumentTypeError
import re

from libvrt.bad import BadData

def maptype(text):
    if re.fullmatch('([a-zA-Z_][a-zA-Z0-9_.]*'
                    '=[a-zA-Z_][a-zA-Z0-9_.]*/?'
                    '|[, ])*',
                    text):
        return text.encode('UTF-8')
    raise ArgumentTypeError('malformed name pairs: {}'
                            .format(repr(text)))

def parsemaps(option, *, default = False):
    '''Parse an option value that specifies mappings from old names to new
    names. The argument is a list of byte strings that consist of any
    number of pairs in the form b'old=new' separated by any number
    commas or spaces (or both). If default is True, every "old" must
    be of the form "vk" where "k" is the canonical written
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
