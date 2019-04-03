from argparse import ArgumentTypeError
from itertools import chain
import re

from vrtargslib import BadData

# Regular expression recognizing a valid extended field name suffix
_xrest_exp = R'[a-z0-9_.-]+ /?'
# Regular expression recognizing a valid extended field name
_xname_exp = R'(?![\d.-]) ' + _xrest_exp

def isxname(s):
    '''Test that the argument string is valid as an extended field name in
    VRT. Valid field names in VRT consist of ASCII letters, digits,
    underscores and hyphens, and start with a letter or an underscore.
    Extended names may also contain ASCII periods (but still start
    with a letter or an underscore) and may end with a slash to indicate
    a feature-set attribute.

    '''
    # Even though cwb-encode can encode attributes with names beginning
    # with a hyphen, CQP apparently cannot use them in (at least as of
    # CWB 3.4.10). A name starting with a hyphen might not be a good idea
    # anyway, so we do not allow them.
    return re.fullmatch(_xname_exp, s, re.ASCII | re.VERBOSE)

def isxrest(s):
    '''Test that the argument is a valid suffix to an extended field name
    in VRT. A suffix may be a valid name or also start with a digit or
    period.

    '''
    return re.fullmatch(_xrest_exp, s, re.ASCII | re.VERBOSE)

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

def xnames(s):
    '''Comma-separated extended field names. Usable as a type in an
    ArgumentParser.

    '''
    names = s.split(',')
    if all(map(isxname, names)):
        return s

    raise ArgumentTypeError('invalid extended names: ' + s)

def binxnames(s):
    '''Comma-separated extended field names in UTF-8. Usable as a type in
    an ArgumentParser.

    '''
    return xnames(s).encode('UTF-8')

_names_exp = R'''
# matches valid extended field name comments
# allowing . in special (temporary) names
# including + as a special name (in "flat" format)

<!-- \s Positional \s attributes:

( \s ''' + _xname_exp + R''' | \s \+ )+

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
        return re.findall(R'[\w+]\S*', nameline)[2:]

    raise BadData('invalid positional-attributes comment')

def binnamelist(nameline):
    if isbinnames(nameline):
        return re.findall(bR'[\w+]\S*', nameline)[2:]

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

def numnameindices(names, *numname, numbase=1):
    '''Return a tuple of the 0-based indices of each numname in names, where
    either names is a list of names as strings and each numname is a string,
    or names is a list of bytes objects and each numname is a bytes object
    (encoded in UTF-8). Alternatively, if a numname is an integer or a numeric
    string or bytes object representing a numbase-based index to names, return
    it as an integer, converted to a 0-based index. numname may also contain
    two numnames separated by a "|": if the first one is not found (raises an
    exception), the second one is tried. Raise an exception if any numname is
    not in the list or, if numeric and names is non-empty, not in range(0,
    len(names)) (taking numbase into account).

    '''

    def getindex_base(names, numname):
        index = -1
        if isinstance(numname, int):
            index = numname - numbase
        elif numname.isdigit():
            index = int(numname) - numbase
        else:
            return names.index(numname)
        if index < 0 or (names and index >= len(names)):
            raise BadData(
                'name index {} out of range {}...{}'
                .format(index + numbase, numbase, len(names) - 1 + numbase))
        return index

    def getindex(names, numname):
        numname_alts = numname.split(
            (b'|' if isinstance(numname, bytes) else '|'), 1)
        for altnum, numname_alt in enumerate(numname_alts):
            try:
                return getindex_base(names, numname_alt)
            except (ValueError, BadData):
                if len(numname_alts) == 1 or altnum > 0:
                    raise
                else:
                    pass

    try:
        return tuple(getindex(names, nm) for nm in numname)
    except ValueError:
        raise BadData('some name of {} is not in list {}'
                      .format(numname, names))

def numnameindex(names, numname, numbase=1):
    '''Return the 0-based index of a numname in a list of names, or if numname
    is an integer or a numeric string (or bytes object), the number converted
    to a 0-based index.
    Raise an exception if the name is not in the list or the numeric index is
    out of range for an index to names.

    '''
    [index] = numnameindices(names, numname, numbase=numbase)
    return index

def extract_numnameindices(lines, *numname, numbase=1):
    '''Return a tuple of the 0-based indices of each numname based on the
    names in the first "Positional attributes" comment found in lines. lines
    and numname may be strings or bytes objects; the types need not be the
    same. Alternatively, if a numname is an integer or a numeric string or
    bytes object representing a numbase-based index to names, return it as an
    integer, converted to a 0-based index. A numname may also contain two
    numnames separated by a "|": if the first one is not found (raises an
    exception), the second one is tried. Raise an exception if any numname is
    not in the list or, if numeric and names is non-empty, not in range(0,
    len(names)) (taking numbase into account).

    '''
    indices = []
    for line in lines:
        bin_line = isinstance(line, bytes)
        if (isbinnames(line) if bin_line else isnames(line)):
            if bin_line:
                line = line.decode()
            names = namelist(line)
            for nm in numname:
                if isinstance(nm, bytes):
                    nm = nm.decode()
                indices.append(numnameindex(names, nm))
            return indices
    return numnameindices([], *numname)

def extract_numnameindex(lines, numname, numbase=1):
    '''Return the 0-based index of a numname based on the names in the first
    "Positional attributes" comment found in lines, or if numname is an
    integer or a numeric string (or bytes object), the number converted to a
    0-based index. Raise an exception if the name is not in the list or the
    numeric index is out of range for an index to names.

    '''
    [index] = extract_numnameindices(lines, numname, numbase=numbase)
    return index

def insertnames(nameline, atname, *afternames):
    '''Return the field-name comment (a string) with afternames inserted
    after atname. Or raise an exception if some aftername is invalid, not new
    or duplicated. A field name is not allowed both with and without a
    trailing slash.

    '''
    fieldnames = namelist(nameline)
    at = nameindex(fieldnames, atname) + 1

    invalid_names = [name for name in afternames
                     if not (isxname(name) or name == '+')]
    if invalid_names:
        raise BadData('new names {} not valid extended field names'
                      .format(invalid_names))
    if len(afternames) != len(set(name.rstrip('/') for name in afternames)):
        raise BadData('duplicates in new names {}'.format(afternames))
    fieldnames_noslash = [name.rstrip('/') for name in fieldnames]
    if any(name.rstrip('/') in fieldnames_noslash for name in afternames):
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
    invalid, not new or duplicated. A field name is not allowed both
    with and without a trailing slash.

    '''
    fieldnames = binnamelist(nameline)
    at = nameindex(fieldnames, atname) + 1

    invalid_names = [name for name in afternames
                     if not (isxname(name.decode('UTF-8')) or name == b'+')]
    if invalid_names:
        raise BadData('new names {} not valid as extended field names'
                      .format(invalid_names))
    if len(afternames) != len(set(name.rstrip(b'/') for name in afternames)):
        raise BadData('duplicates in new names {}'.format(afternames))
    fieldnames_noslash = [name.rstrip(b'/') for name in fieldnames]
    if any(name.rstrip(b'/') in fieldnames_noslash for name in afternames):
        raise BadData('some new name of {} in old names {}'
                      .format(afternames, fieldnames))

    return b' '.join(chain([b'<!-- Positional attributes:'],
                           fieldnames[:at],
                           afternames,
                           fieldnames[at:],
                           [b'-->\n']))
