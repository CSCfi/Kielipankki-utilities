from argparse import ArgumentTypeError
from itertools import chain
import re

from vrtargslib import BadData

def isxname(s):
    '''Test that the argument string is valid as an extended field name in
    VRT. Valid field names in VRT consist of ASCII letters, digits,
    and underscores, and start with a letter or an underscore.
    Extended names may also contain ASCII periods (but still start
    with a letter or an underscore).

    '''
    return re.fullmatch(R' (?![\d.]) [\w.]+ ', s,
                        re.ASCII | re.VERBOSE)

def isxrest(s):
    '''Test that the argument is a valid suffix to an extended field name
    in VRT. A suffix may be a valid name or also start with a digit or
    period.

    '''
    return re.fullmatch(R'[\w.]+', s, re.ASCII | re.VERBOSE)

def xname(s):
    '''Return a valid name (see isxname), or raise an exception. Usable as
    a type in an ArgumentParser.

    '''

    if isxname(s): return s

    raise ArgumentTypeError('not valid as an extended field name: ' + s)

def xrest(s):
    '''Return a valid suffix (see isxrest), or raise an exception. Usable as
    a type in an ArgumentParser.

    '''

    if isxrest(s): return s

    raise ArgumentTypeError('not valid suffix to an extended field name: ' + s)

def binxname(s):
    '''Extended field name in UTF-8. Usable as a type in an
    ArgumentParser.

    '''
    return xname(s).encode('UTF-8')

def binxrest(s):
    '''Suffix an extended field name in UTF-8. Usable as a type in an
    ArgumentParser.

    '''
    return xrest(s).encode('UTF-8')

_names_exp = R'''
# matches valid extended field name comments
# allowing . in special (temporary) names
# including + as a special name (in "flat" format)

<!-- \s Positional \s attributes:

( \s (?![\d.]) [\w.]+ | \s \+ )+

\s --> \r? \n?

'''

_names = re.compile(_names_exp, re.ASCII | re.VERBOSE)

_binnames = re.compile(_names_exp.encode('UTF-8'), re.ASCII | re.VERBOSE)

def isnames(s):
    '''Test if argument string is a valid positional-attributes comment,
    allowing extended field names (see isxname) and + as a field name.

    '''
    return _names.fullmatch(s) is not None

def isbinnames(bs):
    '''Test if argument bytes is a valid positional-attributes comment,
    allowing extended field names (see isxname) and + as a field name.

    '''
    return _binnames.fullmatch(bs) is not None

def namelist(nameline):
    if isnames(nameline):
        return re.findall(R'[\w.+]+', nameline)[2:]

    raise BadData('invalid positional-attributes comment')

def binnamelist(nameline):
    if isbinnames(nameline):
        return re.findall(bR'[\w.+]+', nameline)[2:]

    raise BadData('invalid positional-attributes comment')

def nameindices(names, *name):
    '''Return 0-based index of each name in names, where either names is a
    list of names as strings and each name is a string, or names is a
    list of bytes objects and each name is a bytes object (encoded in
    UTF-8). Or raise an exception if any name is not in the list.

    '''
    try:
        return tuple(names.index(nm) for nm in name)
    except ValueError:
        raise BadData('some name of {} is not in list {}'
                      .format(name, names))

def nameindex(names, name):
    '''Return 0-based index of a name in a list of names, or raise an
    exception if the name is not in the list.

    '''
    [index] = nameindices(names, name)
    return index

def insertnames(nameline, atname, *afternames):
    '''Return the field-name comment (a string) with afternames inserted
    after atname. Or raise an exception if some aftername is not new.

    '''
    fieldnames = namelist(nameline)
    at = nameindex(fieldnames, atname) + 1

    if any(name in fieldnames for name in afternames):
        raise BadData('some new name of {} in old names {}'
                      .format(afternames, fieldnames))

    return ' '.join(chain(['<!-- Positional attributes:'],
                          fieldnames[:at],
                          afternames,
                          fieldnames[at:],
                          ['-->\n']))

def bininsertnames(nameline, atname, *afternames):
    '''Return the field-name comment (a bytes object) with afternames
    inserted after atname. Or raise an exception if some aftername is
    not new.

    '''
    fieldnames = binnamelist(nameline)
    at = nameindex(fieldnames, atname) + 1

    if any(name in fieldnames for name in afternames):
        raise BadData('some new name of {} in old names {}'
                      .format(afternames, fieldnames))

    return b' '.join(chain([b'<!-- Positional attributes:'],
                           fieldnames[:at],
                           afternames,
                           fieldnames[at:],
                           [b'-->\n']))
