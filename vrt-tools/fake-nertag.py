import sys
from random import choice, randrange, sample
pop = (b'<Foo>', b'<Foo',
       b'</Bar>', b'</Bar>',
       b'<Foo/>', b'<Baz/>',
       b'', b'', b'', b'', b'')
for line in sys.stdin.buffer:
    if line.isspace():
        sys.stdout.buffer.write(line)
        continue
    line = line.rstrip(b'\r\n')
    sys.stdout.buffer.write(line)
    sys.stdout.buffer.write(b'\t')
    sys.stdout.buffer.write(choice(pop)
                            if '--max' in sys.argv else
                            choice((b'B-X', b'B-Y', b'I-X', b'O', b'O'))
                            if '--bio' in sys.argv else
                            b'\t'.join(sample(pop, randrange(4))))
    sys.stdout.buffer.write(b'\n')
