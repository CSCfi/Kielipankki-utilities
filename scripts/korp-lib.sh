# -*- coding: utf-8 -*-

# A top-level library for loading shlib components containing common
# functions and initialization code for Bourne shell (or Bash)
# scripts, mostly related to Korp corpus import.
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# $scriptdir is the (main) directory for scripts (also containing this
# file): needed instead of $progdir for scripts in the subdirectories
# of corp/ to be able to run scripts in the main script directory.
# NOTE that this only works for Bash; for sh scripts, you need to set
# scriptdir manually in the main script if it is not the same as
# $progdir.
if [ "x$scriptdir" = x ]; then
    if [ "x$BASH_VERSION" != x ]; then
	scriptdir=$(dirname "${BASH_SOURCE[0]}")
    else
	scriptdir=$progdir
    fi
fi

# Source all shlib components
shlib_required_libs=${shlib_required_libs:-"base site cleanup str msgs file sys opts times vrt cwb mysql kielipankki"}
. $scriptdir/shlib/loadlibs.sh
