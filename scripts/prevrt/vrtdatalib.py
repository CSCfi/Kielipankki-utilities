import re

def asrecord(line):
    '''Strip and split into its fields a VRT data line given as a
    string.

    '''
    return line.rstrip('\n').split('\t')

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
    return line.rstrip(b'\n').split(b'\t')

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
