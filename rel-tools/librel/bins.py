import shutil

SORT = shutil.which('sort')
if SORT is None:
    print('"sort" not found', file = sys.stderr)
    exit(3)
elif SORT not in { '/usr/bin/sort', '/bin/sort' }:
    print('"sort" not trusted:', SORT, file = sys.stderr)
    exit(3)

CAT = shutil.which('cat')
if CAT is None:
    print('"cat" not found', file = sys.stderr)
    exit(3)
elif CAT not in { '/usr/bin/cat', '/bin/cat' }:
    print('"cat" not trusted:', CAT, file = sys.stderr)
    exit(3)

HEAD = shutil.which('head')
if HEAD is None:
    print('"head" not found', file = sys.stderr)
    exit(3)
elif HEAD not in { '/usr/bin/head', '/bin/head' }:
    print('"head" not trusted:', HEAD, file = sys.stderr)
    exit(3)

TAIL = shutil.which('tail')
if TAIL is None:
    print('"tail" not found', file = sys.stderr)
    exit(3)
elif TAIL not in { '/usr/bin/tail', '/bin/tail' }:
    print('"tail" not trusted:', TAIL, file = sys.stderr)
    exit(3)
