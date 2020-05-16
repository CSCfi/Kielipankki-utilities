from itertools import cycle, filterfalse

from libvrt.keeper import keeper as _getter
from libvrt.nameline import isnameline, makenameline

def nameloop(lines, names, *,
             keep = (0, 1, 2),
             sans = False,
             once = False):
    '''Yield the desired number of numbered fake VRT lines, in
    UTF-8. Meta, data with three fields, repeated name comments
    specify the provided names, fields and names modulo keep.

    Good for testing vrt-name, vrt-rename, vrt-keep, vrt-drop.

    With sans == True, filter all name comments out.

    With once == True, filter redundant name comments out.

    '''

    if sans:
        yield from filterfalse(isnameline,
                               nameloop(lines, names, keep = keep))
        return

    if once:
        many = nameloop(lines, names, keep = keep)
        for line in many:
            yield line
            if isnameline(line):
                break
        yield from filterfalse(isnameline, many)
        return

    keeper = _getter(*keep)
    record1 = keeper(('data', '{k}', '{r}'))
    record2 = keeper(('data', '{k}', '{r}'))
    record3 = keeper(('data', '{k}', '{r}'))

    yield from (
        line.format(k = k, r = r).encode('UTF-8')
        for k, r, line
        in zip(range(1, lines + 1),
               cycle((2, 3, 1)),
               cycle(('<meta line="{k}" loop="{r}">\n',
                      makenameline(names).decode('UTF-8'),
                      '\t'.join(record1) + '\n',
                      '\t'.join(record2) + '\n',
                      '\t'.join(record3) + '\n',
                      '</meta>\n')))
    )
