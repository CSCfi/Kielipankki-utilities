# -*- coding: utf-8 -*-

# shlib/loadlibs.sh
#
# Source the libraries listed in $shlib_required_libs unless already
# sourced; may be sourced recursively.


# The following finds the library directory only in Bash; for sh
# scripts, you need to set scriptdir manually in the main script if it
# is not the same as $progdir.
if [ "x$scriptdir" = x ]; then
    if [ "x$BASH_VERSION" != x ]; then
	_shlibdir=$(dirname "${BASH_SOURCE[0]}")
    else
	_shlibdir=$progdir/shlib
    fi
else
    _shlibdir=$scriptdir/shlib
fi


# Source only libraries not yet sourced

_shlib_sourced_libs=${_shlib_sourced_libs:-:}
for _lib in $shlib_required_libs; do
    if [ "$_shlib_sourced_libs" = ":" ] ||
	[ "${_shlib_sourced_libs##*:$_lib:*}" != "" ];
    then
	_shlib_sourced_libs="$_shlib_sourced_libs$_lib:"
	. $_shlibdir/$_lib.sh
    fi
done
