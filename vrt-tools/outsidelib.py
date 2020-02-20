# Host detection is rather heuristic; the difference that actually
# matters is the location of various components so testing whether one
# such location exists

import os, sys

if os.path.isdir('/appl/soft/ling/finnish-tagtools'):
    from outside.puhti import *
elif os.path.isdir('/appl/ling/finnish-tagtools'):
    from outside.taito import *
elif False: # True
    print('Alert! in an unrecognized environment')
    print('Alert! in an unrecognized environment', file = sys.stderr)
    from outside.taito import *
else:
    raise ImportError('vrt-tools outsidelib: unrecognized environment')
