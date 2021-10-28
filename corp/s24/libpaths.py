
# libpaths.py
#
# A module adding the locations of VRT Tools and korpimport libraries to
# sys.path.


import os.path
import sys

_libdirs = [
    '../../vrt-tools',
    '../../scripts',
]

_thisdir = os.path.dirname(__file__)
for _libdir in _libdirs:
    sys.path.append(os.path.abspath(os.path.join(_thisdir, _libdir)))
