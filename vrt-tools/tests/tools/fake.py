from itertools import cycle, filterfalse

from libvrt.nameline import isnameline, makenameline

def nameloop(lines, *, sans = False, once = False):
    '''Yield the desired number of numbered fake VRT lines, in
    UTF-8. Meta, data with three fields, repeated name comments.
    Useful for testing vrt-name and vrt-rename (at least).

    With sans == True, filter all name comments out.

    With once == True, filter all redundant name comments out.
    '''

    if sans:
        yield from filterfalse(isnameline, nameloop(lines))
        return

    if once:
        many = nameloop(lines)
        for line in many:
            yield line
            if isnameline(line):
                break
        yield from filterfalse(isnameline, many)
        return
        
    yield from (
        line.format(k = k, r = r).encode('UTF-8')
        for k, r, line
        in zip(range(1, lines + 1),
               cycle((2, 3, 1)),
               cycle(('<meta line="{k}" loop="{r}">\n',
                      makenameline(b'word line loop'.split())
                      .decode('UTF-8'),
                      'data\t{k}\t{r}\n',
                      'data\t{k}\t{r}\n',
                      'data\t{k}\t{r}\n',
                      '</meta>\n')))
    )
