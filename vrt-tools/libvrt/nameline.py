# -*- mode: Python; -*-

'''Support the handling of the name lines encountered in VRT.'''

import re

from libvrt.bad import BadData

def isnameline(line):
    return line.startswith(b'<!-- #vrt positional-attributes: ')

def makenameline(names):
    return b' '.join((b'<!-- #vrt positional-attributes:',
                      *names, b'-->\n'))

def parsenameline(line, *, required = ()):
    '''Parse a nameline (a byte string) into a list of the names.
    Optionally require that the required names are among the names
    found in the line, possibly with a trailing slash (no trailing
    slashes in required but they may occur with one in line).

    Return the name list, or raise a BadData exception.

    Used by vrt-rename, vrt-keep, vrt-drop, at least.

    '''

    # drop b'<!-- #vrt positional-attributes:' and '-->\n'
    names = re.findall(b'[a-zA-Z_][a-zA-Z0-9_.]*/?', line)[3:]

    # require the required
    bad = sorted(set(required) -
                 set(name.rstrip(b'/') for name in names))
    if bad:
        raise BadData('required {}: {}'
                      .format(b' '.join(bad).decode('UTF-8'),
                              b' '.join(names).decode('UTF-8')))

    return names

def rename(names, mapping):
    '''Replace any of the old names (that may have a trailing slash) with
    those specified in the mapping. The old names come in a list. The
    mapping comes as a dict (and may specify a trailing slash for any
    new name).

    Do not allow duplicates in the new names, ignoring any trailing
    slash.

    Return new names, or raise a BadData exception.

    '''

    new = [ mapping.get(key.rstrip(b'/'), key) for key in names ]

    bar = [ key.rstrip(b'/') for key in new ]
    bad = sorted(set(key for key in bar if new.count(key) > 1))
    if bad:
        raise BadData('duplicate new names: {}: {}'
                      .format(b' '.join(bad).decode('UTF-8'),
                              b' '.join(new).decode('UTF-8')))

    return new
