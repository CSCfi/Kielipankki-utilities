
# libpaths.py
#
# A module containing a function to append directories to sys.path, so
# that library modules can found in them.


from collections.abc import Sequence

import os.path
import sys


def append_libdirs(libdirs: str | Sequence[str], relative: str | None = None):
    """Append the directories in `libdirs` to `sys.path`.

    `libdirs` can be a single string (single directory) or an iterable
    of strings (directories). The directories can be relative to the
    directory of `relative` which must be an absolute path; by
    default, relative to the directory of this module.

    This function is to be called before importing modules in
    directories in `libdirs` that are not under this directory.
    """
    thisdir: str = os.path.dirname(relative or __file__)
    if isinstance(libdirs, str):
        libdirs = [libdirs]
    for libdir in libdirs:
        sys.path.append(os.path.abspath(os.path.join(thisdir, libdir)))
