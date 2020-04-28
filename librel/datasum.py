import os
from tempfile import mkstemp

from .args import BadData
from .data import getter, records, readhead
from .names import makenames

def sumfile(ins1, ins2, *, rest = (), tag):
    '''Concatenate the two or more input relations in a new temp file in
    TMPDIR, fields in the order they happen to have in the first input
    relation, tagged with the number of the input file (1, 2, ...) in
    a final new field. Return the pathname of the temp file.

    The input relations must have the same names in their head. The
    tag name must be new.

    Sum file is used to implement the Boolean operations on relations,
    in addition to the (tagged) sum of relations. (Sum itself does not
    need a temp file but this way there is only one implementation.
    The point of the temp file is so that all input relations can be
    made to form one concatenated input stream that can be passed to a
    subprocess, even when one of the original inputs was stdin.)

    '''

    [tag] = makenames([tag]) # sanity clause (and UTF-8)

    fd, ouf = mkstemp(prefix = 'relsum', suffix = '.tsv.tmp')
    os.close(fd)

    head1 = readhead(ins1)

    if tag in head1:
        raise BadData('tag is old: ' + tag.decode('UTF-8'))

    def checkhead(insk):
        '''Read head from insk ensuring full match with head1.'''
        headk = readhead(insk, old = head1)
        bad = b' '.join(name for name in headk if name not in head1)
        if bad:
            raise BadData('not in head: ' + bad.decode('UTF-8'))

        return headk

    def append(ins, ous, permute, tk):
        '''Append the permuted body from ins to ous with the byte string tk
        appended to each record as a tag of origin.

        '''

        for r in records(ins):
            ous.write(b'\t'.join(permute(r)))
            head1 and ous.write(b'\t')
            ous.write(tk)
            ous.write(b'\n')

    try:
        head2 = checkhead(ins2)
        get1 = getter(tuple(map(head1.index, head1)))
        get2 = getter(tuple(map(head2.index, head1)))
        with open(ouf, 'wb') as ous:
            ous.write(b'\t'.join(head1))
            head1 and ous.write(b'\t')
            ous.write(tag)
            ous.write(b'\n')
            append(ins1, ous, get1, b'1')
            append(ins2, ous, get2, b'2')
            for k, path in enumerate(rest, start = 3):
                with open(path, 'rb') as insk:
                    tk = str(k).encode('UTF-8')
                    headk = checkhead(insk)
                    getk = getter(tuple(map(headk.index, head1)))
                    append(insk, ous, getk, tk)
    except Exception:
        os.remove(ouf)
        raise

    return ouf
