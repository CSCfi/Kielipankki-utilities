'''Support for field name arguments in relation tools (rel tools).'''

import re

def makenames(args):
    ''' '''

    # allow commas and spaces in individual arguments, split at runs
    names = (
        ' '.join(args.names).replace(',', ' ')
        .encode('UTF-8')
        .split()
    )

    return names

def fillnames(names, n):
    '''Append generated field names of the form "vK" with 1-based field
    number K to have at least n names.

    '''
    
    while n > len(names):
        names.append('v{}'.format(len(names) + 1).encode('utf-8'))

def checknames(names):
    '''Raise an exception if names are not valid as such: not sufficiently
    like identifiers, or not unambiguous.

    '''
    
    bad = [
        name for name in names
        if not re.fullmatch(b'[a-zA-Z_.][a-zA-Z0-9_.]*', name)
    ]

    if bad:
        raise BadData('unhappy names: ' + repr(bad))

    if len(set(names)) < len(names):
        raise BadData('duplicate names')
