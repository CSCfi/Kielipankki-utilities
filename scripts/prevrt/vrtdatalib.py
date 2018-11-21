import re

def asrecord(line):
    '''Strip and split into its fields a VRT data line given as a
    string.

    '''
    return line.rstrip('\r\n').split('\t')

def lineref(line, k):
    '''Return the literal string value, at a 0-based field index, from a
    VRT data line given as a string.

    '''
    return asrecord(line)[k]

def linerefs(line, *ks):
    '''Return the tuple of literal string values, at each 0-based field
    index, from a VRT data line given as a string.

    '''
    record = asrecord(line)
    return tuple(record[k] for k in ks)

def binasrecord(line):
    '''Strip and split into its fields a VRT data line given as a bytes
    object in UTF-8.

    '''
    return line.rstrip(b'\r\n').split(b'\t')

def binlineref(line, k):
    '''Return the literal string values, at a 0-based field index, from a
    VRT data line given as a bytes object in UTF-8).

    '''
    return binasrecord(line)[k]

def binlinerefs(line, *ks):
    '''Return the tuple of literal string values, at each 0-based field
    index, from a VRT data line given as a bytes object in UTF-8.

    '''
    record = binasrecord(line)
    return tuple(record[k] for k in ks)

_strcode = str.maketrans({
    '&' : '&amp;',
    '<' : '&lt;',
    '>' : '&gt;',
})

_bincode = {
    b'&' : b'&amp;',
    b'<' : b'&lt;',
    b'>' : b'&gt;',
}

def _binescape(mo):
    return _bincode[mo.group()]

def escape(value):
    return value.translate(_strcode)

def binescape(value):
    return re.sub(b'[&<>]', _binescape, value)

_strdecode = {
    '&amp;' : '&',
    '&lt;' : '<',
    '&gt;' : '>',
}

_bindecode = {
    b'&amp;' : b'&',
    b'&lt;' : b'<',
    b'&gt;' : b'>',
}

def _strunescape(mo):
    return _strdecode[mo.group()]

def _binunescape(mo):
    return _bindecode[mo.group()]

def unescape(value):
    return re.sub('&(amp|lt|gt);', _strunescape, value)

def binunescape(value):
    return re.sub(b'&(amp|lt|gt);', _binunescape, value)

def nextof(groups, expected0, expected = None):
    '''Return the next group from the groups source if it is of the
    expected kind, or the next two groups if the second kind is not
    None and the next group is of the optional first kind but not of
    the required second kind.

    Raise BadData exception if there are no more groups or the next
    groups are not of the expected kinds.

    When an optional first group is requested, it is reified as a
    list. The list is empty if the next group is of the second kind.

    '''

    if expected is None:
        expected0, expected = None, expected0

    observed, group = next(groups, (None, None))
    if group is None:
        raise BadData('no group available')

    if observed == expected:
        return group if expected0 is None else ([], group)

    if expected0 is None:
        raise BadData('unexpected group')

    if  observed != expected0:
        raise BadData('unexpected first group')

    observed0, group0 = observed, list(group)
    observed, group = next(groups, (None, None))
    if group is None:
        raise BadData('no second group available')

    if observed == expected:
        return group0, group

    raise BadData('unexpected second group')

def next1of(groups, expected0, expected = None):
    '''Return the sole element of the next group from the groups source if
    it is of the expected kind, or the optional first group and the
    sole element of second group if the second expected kind is not
    None and the next group is of the optional first expected kind but
    not of the required second kind.

    Raise BadData exception if there are no more groups or the next
    groups are not of the expected kinds or there are more than one
    elements in the required group.

    When an optional first group is requested, it is reified as a
    list. The list is empty if the next group is of the second kind.

    '''
    if expected is None:
        group = nextof(groups, expected0)
    else:
        list0, group = nextof(groups, expected0, expected)

    element = next(group)
    try:
        next(group)
        raise BadData('more than one element')
    except StopIteration:
        pass

    if expected is None:
        return element
    else:
        return list0, element
