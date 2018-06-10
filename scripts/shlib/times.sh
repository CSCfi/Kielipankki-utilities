# -*- coding: utf-8 -*-

# shlib/times.sh
#
# Generic library functions for Bourne shell scripts: timing functions
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# Load shlib components for the definitions used
shlib_required_libs="base"
. $_shlibdir/loadlibs.sh


# Functions

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
                print >> "/dev/stderr"
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


# Initialize variables

show_times=
