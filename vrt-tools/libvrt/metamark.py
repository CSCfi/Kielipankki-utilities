'''Support library for vrt tools.

'''

from argparse import ArgumentTypeError
import re


def marktype(arg):
    '''Type-check a command line argument as a piece of string that may be
    safe to insert into a value. Encode and return the argument in UTF-8.

    The allowed collection of characters contains ASCII letters and
    digts, round and curly brackets, and some other punctuation, but
    no whitespace characters, emphatically no vertical whitespace
    whatsoever and no tab (HT).

    Intended as a type specification in an ArgumentParser.

    '''

    if re.fullmatch(r'[A-Za-z0-9(){}:;.,_!?/+\-]*', arg):
        return arg.encode('UTF-8')

    raise ArgumentTypeError('not a safe mark: {}'.format(repr(arg)))
