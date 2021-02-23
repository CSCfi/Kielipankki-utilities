'''Find libvrt/ and tests/ in a directory a a few levels above,
prepend that directory (presumed vrt-tools/) to sys.path. So a test
tool script can find library modules.

'''

import os, sys

home = os.path.dirname(os.path.realpath(__file__))
for _ in range(10):
    if ( os.path.isdir(os.path.join(home, 'libvrt')) and
         os.path.isdir(os.path.join(home, 'tests')) ):
        break
    else:
        home = os.path.dirname(home)
else:
    raise FileNotFoundError('looking for ... with libvrt/,tests/ in it')

if home not in sys.path:
    sys.path.insert(0, home)
