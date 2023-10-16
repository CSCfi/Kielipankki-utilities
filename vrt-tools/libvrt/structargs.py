# -*- mode: Python; -*-

'''Support the parsing of command line options that pertain to
structural attribute names (names of structures and their attributes,
or in CWB terminology, names of structural attributes and their
annotations).

'''

from argparse import ArgumentTypeError
import re

from libvrt.bad import BadData

def _structattrbagtype(text, allowany=False):
    # struct_attr | struct : attr (, attr)*
    anyre = '|\\*' if allowany else ''
    structnamere = f'(?:[a-zA-Z][a-zA-Z0-9]*{anyre})'
    # attrnamere also covers style "structname_attrname"
    attrnamere = f'(?:[a-zA-Z_][a-zA-Z0-9_.]*/?{anyre})'
    namere = rf'(?:{structnamere}\s*:\s*)?{attrnamere}'
    sepre = '[,\s]+'
    text = text.strip()
    if re.fullmatch(fr'{namere}({sepre}{namere})*', text):
        return text.encode('UTF-8')
    raise ArgumentTypeError(
        'not structural attribute names: {}'.format(repr(text)))

def structattrbagtype(text):
    '''List of structural attributes separated by spaces or commas,
    structure and its attributes separated by a colon.
    '''
    return _structattrbagtype(text, False)

def structattranybagtype(text):
    '''As structattrbagtype, but allow * to denote any.
    '''
    return _structattrbagtype(text, True)

def parsestructattrs(option, attrstype=list, valuetype=bytes):
    '''Parse an option value that specifies structural attribute names.
    The argument is a list of byte strings that consist of any number
    of structural attribute names separated by any number of commas or
    spaces (or both). A structural attribute can be specified as
    struct_attr or struct:attr. "a:b c d" is interpreted as "a_b a_c
    a_d", whereas "a:b c:d" is interepreted as "a_b c_d" and "a:b c_d"
    as "a_b a_c_d".

    Returns a dict of lists (or sets) of bytes (or str):
    {b'struct1': [b'attr1', b'attr2'], b'struct2': [b'attr3']}.

    attrstype is the type of dict values: list (default) or set (or a
    subclass of either).

    valuetype is the type of names: bytes (default) or set.

    An empty list is allowed. The list is not checked for duplicates.

    '''
    if issubclass(attrstype, list):
        additem = lambda list_, item: list_.append(item)
    elif issubclass(attrstype, set):
        additem = lambda set_, item: set_.add(item)
    else:
        raise ValueError('attrstype must be (a subclass of) list or set')

    if valuetype is bytes:
        decode = lambda b: b
    elif valuetype is str:
        decode = lambda b: b.decode('UTF-8')
    else:
        raise ValueError('valuetype must be bytes or str')

    structlist = (b' '.join(option)
                  .replace(b',', b' ')
                  # colons as separate items
                  .replace(b':', b' : ')
                  .split())

    result = {}
    # structure name specified before a colon
    structprefix = None

    listlen = len(structlist)
    idx = 0
    while idx < listlen:
        item = structlist[idx]
        if idx + 2 < listlen and structlist[idx + 1] == b':':
            # next item is a colon and it is followed by another item,
            # so this is structure name
            structprefix = item
            if b'_' in structprefix:
                raise BadData('structure name may not contain underscore: {}'
                              .format(structprefix.decode('UTF-8')))
            idx += 2
            continue
        elif item == b':':
            # colon at the beginning or end or after another colon
            if idx == 0:
                msg = 'colon at the beginning'
            elif idx == listlen - 1:
                msg = 'colon at the end'
            else:
                msg = 'consecutive colons'
            raise BadData(f'invalid structural attribute list: {msg}: "'
                          + b' '.join(option).decode('UTF-8') + '"')
        elif structprefix is None:
            # no colon seen, so this item should be struct_attr
            struct, _, attr = item.partition(b'_')
            if attr == b'':
                raise BadData('no attribute for structure: {}'
                              .format(struct.decode('UTF-8')))
        else:
            # this item is attr in previously specified struct
            struct = structprefix
            attr = item
        struct = decode(struct)
        result.setdefault(struct, attrstype())
        additem(result[struct], decode(attr))
        idx += 1

    return result
