'''Support for field name arguments in relation tools (rel tools).'''

import re

from .bad import BadData

def makenames(spec):
    ''' '''

    # allow commas and spaces in individual arguments, split at runs
    names = (
        ' '.join(spec).replace(',', ' ')
        .encode('UTF-8')
        .split()
    )

    checknames(names) # sanity clause
    return names

def fillnames(names, n):
    '''Append generated field names of the form "vK" with 1-based field
    number K to have at least n names.

    '''

    while n > len(names):
        names.append('v{}'.format(len(names) + 1).encode('utf-8'))

def makerenames(spec):
    ''' '''

    pairs = (
        ' '.join(spec).replace(',', ' ')
        .encode('UTF-8')
        .split()
    )

    # grumble
    pattern = b'[a-zA-Z_.][a-zA-Z0-9_.]*=[a-zA-Z_.][a-zA-Z0-9_.]*'
    bad = [
        pair for pair in pairs
        if not re.fullmatch(pattern, pair)
    ]

    if bad:
        # not safe to decode so use repr instead
        what = [repr(b).lstrip('b') for b in bad]
        raise BadData('unhappy pairs: ' + ' '.join(what))

    pairs = [pair.split(b'=') for pair in pairs]

    mapping = dict(pairs)

    if len(mapping.keys()) < len(pairs):
        bag = [ o for o, n in pairs ]
        dup = sorted(set(o for o in bag if bag.count(o) > 1))
        raise BadData('dup in old: ' + b' '.join(dup).decode('UTF-8'))

    if len(set(mapping.values())) < len(pairs):
        bag = [n for o, n in pairs ]
        dup = sorted(set(o for o in bag if bag.count(o) > 1))
        raise BadData('dup in new: ' + b' '.join(dup).decode('UTF-8'))

    return mapping

def checknames(names):
    '''Raise an exception if names are not valid as such: not sufficiently
    like identifiers, or not unambiguous.

    '''

    bad = [
        name for name in names
        if not re.fullmatch(b'[a-zA-Z_.][a-zA-Z0-9_.]*', name)
    ]

    if bad:
        # not safe to decode so use repr instead
        what = [repr(b).lstrip('b') for b in bad]
        raise BadData('unhappy names: ' + ' '.join(what))

    if len(set(names)) < len(names):
        dup = sorted(set(n for n in names if names.count(n) > 1))
        raise BadData('dup in names: ' + b' '.join(dup).decode('UTF-8'))
