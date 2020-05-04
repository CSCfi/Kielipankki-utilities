'''Support library for vrt tools.

'''

from argparse import ArgumentTypeError
import re

def nametype(arg):
    '''Type-check a command line argument as a single attribute/field
    name. Encode and return the argument in UTF-8.

    Intended as a type specification in an ArgumentParser.

    '''

    name = arg.encode('UTF-8')
    if isname(name): return name
    raise ArgumentTypeError('not a field name: {}'.format(repr(name)))

def isname(name):
    return re.fullmatch(br'[A-Za-z_][A-Za-z0-9._]*', name)
