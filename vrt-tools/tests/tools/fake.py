from itertools import cycle

def nameloop(lines, *, sans = False):
    '''Yield the desired number of numbered fake VRT lines, in
    UTF-8. Meta, data with three fields, repeated name comments.
    Useful for testing vrt-name and vrt-rename (at least).

    With sans == True, with the name comments filtered out.

    '''

    if sans:
        yield from (
            line for line in nameloop(lines)
            if not line.startswith(b'<!-- #vrt positional-attributes: '))
        return

    yield from (
        line.format(k = k, r = r).encode('UTF-8')
        for k, r, line
        in zip(range(1, lines + 1),
               cycle((2, 3, 1)),
               cycle(('<meta line="{k}" loop="{r}">\n',
                      (
                          '<!-- #vrt positional-attributes: '
                          'word line{k} loop{r} -->\n'
                      ),
                      'data\t{k}\t{r}\n',
                      'data\t{k}\t{r}\n',
                      'data\t{k}\t{r}\n',
                      '</meta>\n')))
    )
