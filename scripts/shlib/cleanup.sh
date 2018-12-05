# -*- coding: utf-8 -*-

# shlib/cleanup.sh
#
# Generic library functions for Bourne shell scripts: cleanup
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# Load shlib components for the definitions used
shlib_required_libs="base"
. $_shlibdir/loadlibs.sh


# kill_descendants [--and-self] [-SIG] pid [...]
#
# Kill all the descendant processes of the process(es) with the pid(s)
# listed. If --and-self is specified, also kill the processes
# themselves. If -SIG is specified, it is passed to kill.
#
# Adapted from https://stackoverflow.com/a/26966800
kill_descendants () {
    local self sig pids pid children
    self=
    sig=
    if [ "x$1" = "x--and-self" ]; then
	self=1
	shift
    fi
    if [ "${1#-}" != "$1" ]; then
	sig=$1
	shift
    fi
    pids="$@"
    for pid in $pids; do
	children=$(pgrep -P $pid)
	if [ "x$children" != x ]; then
            kill_descendants --and-self $sig $children
        fi
    done
    if [ "x$self" != x ]; then
	kill $sig $pids
	# According to https://stackoverflow.com/a/5722874, this
	# should prevent the "Terminated" messages from background
	# processes, but it does not seem to. What would work?
	wait $pids 2> /dev/null
    fi
}

# cleanup
#
# Call call_cleanup_funcs, remove temporary files unless
# $cleanup_on_exit is empty or $SHLIB_KEEP_TEMPFILES is non-empty, and
# kill descendant processes.
cleanup () {
    call_cleanup_funcs
    if [ "x$tmp_prefix" != "x" ] && [ "x$cleanup_on_exit" != x ] &&
	   [ "x$SHLIB_KEEP_TEMPFILES" = x ];
    then
	rm -rf $tmp_prefix.*
    fi
    # Register a no-op handler for SIGTERM, so that kill does not
    # trigger it recursively
    trap ':' TERM
    # Kill all the descendant processes of the running script. If the
    # script is a part of a pipe, this avoids killing the other
    # processes in the pipe, as killing by process group would do.
    kill_descendants $$ 2> /dev/null
}

cleanup_abort () {
    cleanup
    exit 1
}


# add_cleanup_funcs function ...
#
# Add function(s) to (the end of) the list of functions be called at
# clean-up (before other clean-up actions).
add_cleanup_funcs () {
    _cleanup_funcs="$_cleanup_funcs $@ "
}

# rm_cleanup_funcs function ...
#
# Remove function(s) from the list of functions to be called at
# cleanup.
rm_cleanup_funcs () {
    local fn
    for fn in "$@"; do
	_cleanup_funcs="${_cleanup_funcs% $fn *}${_cleanup_funcs#* $fn }"
    done
}

# call_cleanup_funcs
#
# Call the functions whose names are listed in $_cleanup_funcs.
call_cleanup_funcs () {
    local fn
    # Use the case statement instead of testing with ${//} to work in
    # (d)ash.
    case "$_cleanup_funcs" in
	*[!" "]* )
	    for fn in $_cleanup_funcs; do
		$fn
	    done
	    ;;
    esac
}


if [ "x$debug" != x ]; then
    cleanup_on_exit=
else
    cleanup_on_exit=1
fi


_cleanup_funcs=


trap cleanup 0
trap cleanup_abort 1 2 13 15
