# -*- coding: utf-8 -*-

# shlib/msgs.sh
#
# Generic library functions for Bourne shell scripts: messages and
# exiting
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# warn msg
#
# Print msg (prefixed with progname and "Warning") to stderr.
#
# If $warn_hook is non-empty, evaluate it with the message as $msg.
warn () {
    local msg
    if [ "x$warn_hook" != x ]; then
	msg=$1
	eval "$warn_hook"
    fi
    echo "$progname: Warning: $1" >&2
}

# error [exitcode] msg
#
# Print msg (prefixed with progname) to stderr and exit with exitcode
# (default: 1).
#
# If $error_hook is non-empty, evaluate it with the message in $msg
# and exit code in $exitcode.
error () {
    local exitcode msg
    exitcode=1
    if [ $# -gt 1 ]; then
	exitcode=$1
	shift
    fi
    if [ "x$error_hook" != x ]; then
	msg=$1
	eval "$error_hook"
    fi
    safe_echo "$progname: $1" >&2
    exit $exitcode
}

# lib_error [exitcode] msg
#
# Library error: Print msg (prefixed with korp-lib.sh) to stderr and
# exit with exitcode (default: 1).
#
# TODO: Allow choosing (via a variable) whether library errors are
# fatal (exit) or, output a warning but continue or are ignored.
lib_error () {
    local exitcode
    exitcode=1
    if [ $# -gt 1 ]; then
	exitcode=$1
	shift
    fi
    safe_echo "korp-lib.sh: $1" >&2
    exit $exitcode
}

# exit_on_error [--message msg] cmd [args ...]
#
# If cmd returns a non-zero, propagate the error and exit with the
# exit code returned by cmd. Print the message specified with
# --message, or a default one.
exit_on_error () {
    local msg _exit_code
    msg=
    if [ "x$1" = "x--message" ]; then
	msg="$2"
	shift 2
    fi
    "$@"
    _exit_code=$?
    if [ $_exit_code != 0 ]; then
	if [ "x$msg" = x ]; then
	    msg="Terminating due to errors in subprocess $1 (exit code $_exit_code)"
	fi
	error $_exit_code "$msg"
    fi
}

# exit_if_error exitcode
#
# If exitcode is non-zero, exit with it. This function can be used
# when the call of a function fn that may exit using function "error"
# is within $(...) but the output of which should saved, since an exit
# in such as subprocess does not exit the parent: $(fn ...);
# exit_if_error $?
exit_if_error () {
    if [ "x$1" != "x0" ]; then
	exit $1
    fi
}

# safe_echo [args ...]
#
# Echo the arguments more safely using printf. Prints the arguments
# even if the first argument contains an option recognized by echo.
safe_echo () {
    if [ $# -gt 0 ]; then
	printf "%s" "$1"
	shift
	if [ $# -gt 0 ]; then
	    printf " %s" "$@"
	fi
    fi
    printf "\n"
}

# test_verbose [level]
#
# Test if $verbose is set and non-zero, or if level is in 0...9 and
# $verbose is greater than or equal to it.
test_verbose () {
    [ "x$verbose" != x ] && [ "x$verbose" != x0 ] &&
    { [ "x$1" = x ] || [ $verbose -ge "0$1" ]; }
}

# verbose [level] cmd [args ...]
#
# If $verbose is set and non-zero, or if level is in 0...9 and
# $verbose is greater than or equal to it, call cmd with args as
# parameters.
verbose () {
    _verbose_level=
    case $1 in
	[0-9] )
	    _verbose_level=$1
	    shift
	    ;;
    esac
    if test_verbose $_verbose_level; then
	_cmd=$1
	shift
	$_cmd "$@"
    fi
}

# echo_verb [--stderr] [level] [args ...]
#
# Echo args (using safe_echo) if $verbose is level (0...9) or greater,
# or if level is not defined, if $verbose is set and non-zero. If
# --stderr is specified, write to stderr.
echo_verb () {
    local stderr _echo_verb_level
    stderr=
    _echo_verb_level=
    if [ "x$1" = "x--stderr" ]; then
	stderr=1
	shift
    fi
    case $1 in
	[0-9] )
	    _echo_verb_level=$1
	    shift
	    ;;
    esac
    # Could we maybe use exec to duplicate the appropriate output file
    # descriptor to avoid the if here?
    if [ "x$stderr" = x ]; then
	verbose $_echo_verb_level safe_echo "$@"
    else
	verbose $_echo_verb_level safe_echo "$@" >&2
    fi
}

# cat_verb [level]
#
# Print the input (using cat) if $verbose is level (0...9) or greater,
# or if level is not defined, if $verbose is set and non-zero.
cat_verb () {
    _verbose_level=
    case $1 in
	[0-9] )
	    _verbose_level=$1
	    shift
	    ;;
    esac
    if test_verbose $_verbose_level; then
	_outfile=/dev/stdout
    else
	_outfile=/dev/null
    fi
    cat > $_outfile
}

# Echo the parameters quoted to standard error if $debug is non-empty.
# TODO: Support debug levels, similarly to verbose above.
echo_dbg () {
    if [ "x$debug" != x ]; then
	for _arg in "$@"; do
	    printf "%s " "'$_arg'" >> /dev/stderr
	done
	printf "\n" >> /dev/stderr
    fi
}

# quote_args args ...
#
# Print each argument in args: arguments containing spaces, quotes or
# other shell metacharacters are enclosed in single quotes, with
# single quotes themselves converted to '"'"'. Unlike quote_args_safe
# (below), quote_args does not quote arguments not containing any of
# these characters.
#
# TODO: Check if the list of shell metacharacters to be quoted is
# complete. If it is, this function could always be used instead of
# quote_args_safe.
# FIXME: The result contains a trailing space.
quote_args () {
    local arg
    for arg in "$@"; do
	case $arg in
	    *"'"* )
		# Copied from quote_args_safe
		printf "%s" "$arg" | sed "s/'/'\"'\"'/g; s/^\(.*\)$/'&' /"
		;;
	    *[' "`?*<>|\[]$(){}&;=!']* | "" )
		printf "'%s' " "$arg"
		;;
	    * )
		printf "%s " "$arg"
		;;
	esac
    done
}

# quote_args_safe args ...
#
# Print each argument in args enclosed in single quotes, single quotes
# themselves converted to '"'"'. The result may be used to retain
# spaces in arguments in "$(eval command $result)", for example.
#
# Adapted from http://stackoverflow.com/questions/1668649/how-to-keep-quotes-in-args#answer-8723305
#
# FIXME: The result contains a trailing space
quote_args_safe () {
    local arg
    for arg in "$@"; do
	case "$arg" in
            *"'"* )
		printf "%s" "$arg" | sed "s/'/'\"'\"'/g; s/^\(.*\)$/'&' /"
		;;
            * )
		printf "'%s' " "$arg"
		;;
	esac
    done
}

# echo_quoted [args ...]
#
# Like quote_args but print a trailing newline.
echo_quoted () {
    quote_args "$@"
    printf "\n"
}


# Initialize variables

# Code to be evaluated at warn and error
warn_hook=
error_hook=
