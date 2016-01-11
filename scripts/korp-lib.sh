# -*- coding: utf-8 -*-

# Functions and other code common to several Bourne shell scripts
# related to Korp corpus import
#
# NOTE: Some functions require Bash.


# Common functions

find_existing_dir () {
    _test=$1
    _file=$2
    shift 2
    for dir in "$@"; do
	if [ $_test $dir/$_file ]; then
	    echo $dir
	    break
	fi
    done
}

find_filegroup () {
    filegroup=
    for grp in $@; do
	if groups | grep -qw $grp; then
	    filegroup=$grp
	    break
	fi
    done
    if [ "x$filegroup" = x ]; then
	filegroup=`groups | cut -d' ' -f1`
    fi
}

find_prog () {
    # If --no-path is specified, do not try to find the program on
    # $PATH but only in argument directories. Otherwise, try to find
    # the program on $PATH at the position marked with "@" in the
    # argument directory list, or if the arguments do not contain a
    # "@", after any argument directories.
    if [ "x$1" = "x--no-path" ]; then
	shift
    else
	set -- "$@" @
    fi
    _prog=$1
    shift
    for _dir in "$@"; do
	if [ "$_dir" = @ ]; then
	    _path=`which "$_prog" 2> /dev/null`
	    if [ "x$_path" != "x" ]; then
		echo "$_path"
		return 0
	    fi
	elif [ -x "$_dir/$_prog" ]; then
	    echo "$_dir/$_prog"
	    return 0
	fi
    done
    return 1
}

test_file () {
    _test=$1
    _file=$2
    _not_found_cmd=$3
    shift 3
    if [ $_test "$_file" ]; then
	return 0
    else
	$_not_found_cmd "$@"
	return 1
    fi
}

ensure_perms () {
    chgrp -R $filegroup "$@"
    chmod -R g+rwX "$@"
}

warn () {
    echo "$progname: Warning: $1" >&2
}

error () {
    echo "$progname: $1" >&2
    exit 1
}

# exit_on_error cmd [args ...]
#
# If cmd returns a non-zero, propagate the error and exit.
exit_on_error () {
    "$@"
    _exit_code=$?
    if [ $_exit_code != 0 ]; then
	error "Terminating due to errors in subprocess $1 (exit code $_exit_code)"
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
	printf " %s" "$@"
    fi
    printf "\n"
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
    if [ "x$verbose" != x ] && [ "x$verbose" != x0 ] &&
	{ [ "x$_verbose_level" = x ] || [ $verbose -ge $_verbose_level ]; }
    then
	_cmd=$1
	shift
	$_cmd "$@"
    fi
}

# echo_verb [level] [args ...]
#
# Echo args (using safe_echo) if $verbose is level (0...9) or greater,
# or if level is not defined, if $verbose is set and non-zero.
echo_verb () {
    _echo_verb_level=
    case $1 in
	[0-9] )
	    _echo_verb_level=$1
	    shift
	    ;;
    esac
    verbose $_echo_verb_level safe_echo "$@"
}

# Echo the parameters quoted to standard error if $debug is non-empty.
# TODO: Support debug levels, similarly to verbose above.
echo_dbg () {
    if [ "x$debug" != x ]; then
	for _arg in "$@"; do
	    printf "%s " "'$_arg'" > /dev/stderr
	done
	printf "\n" > /dev/stderr
    fi
}

# Output timestamped (ISO date+time and epoch+nanoseconds) text
echo_timestamp () {
    date +"[%F %T %s.%N] $*"
}

# Show subprocess CPU usage information
subproc_times () {
    printf "Subprocess times: "
    # A pipe cannot be used, since each process is run in a separate
    # shell, so the times would be for that shell only.
    times > $tmp_prefix.times
    tail -1 $tmp_prefix.times |
    sed -e 's/m/:/g; s/s//g;'
    rm $tmp_prefix.times
}

# time_cmd_uncond [--format timeformat] command [args]
#
# Print the user and system time used by command with args to stdout,
# using the format timeformat (default: "Times: <command>:
# <times>\n").
#
# NOTE: This only works in Bash, not in Dash, at least not if command
# is a shell function.
time_cmd_uncond () {
    local format
    if [ "x$1" = "x--format" ]; then
	format=$2
	shift
	shift
    else
	format="Times: $1: %s\n"
    fi
    # TIMEFORMAT is used by the Bash built-in, TIME by the GNU time
    # command. NOTE: If calls to time_cmd_uncond are nested, the
    # innermost format is used for the outer commands as well.
    TIMEFORMAT="@@@TIMES: $format"
    TIME="@@@TIMES: $format"
    # The Bash built-in time writes to stderr, but we want to output
    # the times to stdout and the rest of the stderr to stderr.
    local fifo_base=$tmp_prefix.$$.fifo
    local fifo=$fifo_base
    local i=0
    while [ -e $fifo ]; do
	fifo=$fifo_base.$i
	i=$(($i + 1))
    done
    mkfifo $fifo
    awk '{
            if (/^@@@TIMES: /) {
                sub (/@@@TIMES: /, "")
                print
            } else {
                print > "/dev/stderr"
            }
        }' < $fifo &
    local filter_pid=$!
    {
	time "$@"
    } 2> $fifo
    wait $filter_pid
    rm -f $tmp_prefix.$$.fifo
}

# time_cmd [--format timeformat] command [args]
#
# Print the times if the value of $show_times is non-empty.
time_cmd () {
    if [ "x$show_times" != x ]; then
	time_cmd_uncond "$@"
    else
	if [ "x$1" = "x--format" ]; then
	    shift
	    shift
	fi
	"$@"
    fi
}

cleanup () {
    if [ "x$tmp_prefix" != "x" ] && [ "x$cleanup_on_exit" != x ]; then
	rm -rf $tmp_prefix.*
    fi
    # Register a no-op handler for SIGTERM, so that kill does not
    # trigger it recursively
    trap ':' TERM
    # Kill all processes in the process group of the running script.
    # This does not kill processes that have changed their process
    # group (cf.
    # http://stackoverflow.com/questions/360201/kill-background-process-when-shell-script-exit).
    kill -- -$$ 2> /dev/null
}

cleanup_abort () {
    cleanup
    exit 1
}

get_host_env () {
    case $HOSTNAME in
	taito* | c[0-9] | c[0-9][0-9] | c[0-9][0-9][0-9] )
	    echo taito
	    ;;
	korp*.csc.fi )
	    echo korp
	    ;;
	nyklait-09-01* )
	    echo nyklait-09-01
	    ;;
	* )
	    echo unknown
	    ;;
    esac
}

toupper () {
    echo "$1" |
    sed -e 's/\(.*\)/\U\1\E/'
}

comprcat () {
    if [ "x$1" = x ]; then
	cat
    else
	for fname in "$@"; do
	    case "$fname" in
		*.bz2 )
		    bzcat "$fname"
		    ;;
		*.gz )
		    zcat "$fname"
		    ;;
		*.xz )
		    xzcat "$fname"
		    ;;
		*.tar | *.tar.[bgx]z | *.tar.bz2 | *.t[bgx]z | *.tbz2 )
		    tar -xaOf "$fname"
		    ;;
		* )
		    cat "$fname"
		    ;;
	    esac
	done
    fi
}

calc_gib () {
    awk 'BEGIN { printf "%0.3f", '$1' / 1024 / 1024 / 1024 }'
}

get_filesize () {
    ls -l "$1" | awk '{print $5}'
}

# add_prefix prefix args ...
#
# Prepend prefix to all args.
add_prefix () {
    _add_prefix_prefix=$1
    shift
    printf -- "$_add_prefix_prefix%s " "$@"
}

# list_corpora [--on-error error_cmd] registry_dir corpus_id ...
#
# List the corpora in the parameters as found in registry_dir,
# expanding shell wildcards (but not braces). If some listed corpora
# are not found, call error_cmd (default: error) with an error
# message.
list_corpora () {
    _list_corpora_no_error=
    _list_corpora_error_func=error
    if [ "x$1" = "x--on-error" ]; then
	shift
	_list_corpora_error_func=$1
	shift
    fi
    _list_corpora_registry=$1
    shift
    ls $(add_prefix $_list_corpora_registry/ "$@") \
	2> $tmp_prefix.corpid_errors |
    sed -e 's,.*/,,' |
    grep '^[a-z_][a-z0-9_-]*$' > $tmp_prefix.corpids
    if [ -s $tmp_prefix.corpid_errors ]; then
	error_files=$(
	    sed -e 's,^.*cannot access .*/\([^:/]*\):.*$,\1,' \
		< $tmp_prefix.corpid_errors
	)
	$_list_corpora_error_func \
	    "Corpora not found in the CWB corpus registry: $error_files"
    fi
    cat $tmp_prefix.corpids
    rm -rf $tmp_prefix.corpids $tmp_prefix.corpid_errors
}


# Common initialization code

default_corpus_roots=${default_corpus_roots:-"/v/corpora /proj/clarin/korp/corpora $WRKDIR/corpora /wrk/jyniemi/corpora"}

# Root directory, relative to which the corpus directory resides
corpus_root=${CORPUS_ROOT:-$(find_existing_dir -d "" $default_corpus_roots)}

default_cwb_bindirs=${default_cwb_bindirs:-"/usr/local/cwb/bin /usr/local/bin /proj/clarin/korp/cwb/bin $USERAPPL/bin /v/util/cwb/utils"}

# The directory in which CWB binaries reside
cwb_bindir=${CWB_BINDIR:-$(find_existing_dir -e cwb-describe-corpus $default_cwb_bindirs)}

default_korp_frontend_dirs=${default_korp_frontend_dirs:-"/var/www/html/korp /var/www/html"}

# The (main) Korp frontend directory
korp_frontend_dir=${KORP_FRONTEND_DIR:-$(find_existing_dir -e config.js $default_korp_frontend_dirs)}

default_filegroups="korp clarin"
find_filegroup $default_filegroups

tmpdir=${TMPDIR:-${TEMPDIR:-${TMP:-${TEMP:-/tmp}}}}
tmp_prefix=$tmpdir/$progname.$$

# Korp MySQL database
korpdb=korp
# Unless specified via environment variables, assume that the Korp
# MySQL database user and password are specified in a MySQL option
# file
mysql_opts=
if [ "x$KORP_MYSQL_USER" != "x" ]; then
    mysql_opts=--user=$KORP_MYSQL_USER
fi
if [ "x$KORP_MYSQL_PASSWORD" != "x" ]; then
    mysql_opts="$mysql_opts --password=$KORP_MYSQL_PASSWORD"
fi

cleanup_on_exit=1

show_times=


trap cleanup 0
trap cleanup_abort 1 2 13 15


if [ "x$shortopts" != x ]; then
    shortopts="-o $shortopts"
fi
if [ "x$longopts" != x ]; then
    longopts="-l $longopts"
fi

if [ "x$shortopts" != x ] || [ "x$longopts" != x ]; then
    # Test if GNU getopt
    getopt -T > /dev/null
    if [ $? -eq 4 ]; then
	# This requires GNU getopt
	args=`getopt $shortopts $longopts -n "$progname" -- "$@"`
	if [ $? -ne 0 ]; then
	    exit 1
	fi
	eval set -- "$args"
    fi
    # If not GNU getopt, arguments of long options must be separated from
    # the option string by a space; getopt allows an equals sign.
fi
