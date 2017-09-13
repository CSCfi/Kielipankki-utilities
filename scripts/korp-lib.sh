# -*- coding: utf-8 -*-

# Functions and other code common to several Bourne shell scripts
# related to Korp corpus import
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


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
    chgrp -R $filegroup "$@" 2> /dev/null
    chmod -R $fileperms "$@" 2> /dev/null
    return 0
}

# mkdir_perms dir [dir ...]
#
# Create the directories dir and ensure that they have the desired
# permissions ($filegroup and $fileperms).
mkdir_perms () {
    if mkdir -p "$@"; then
	ensure_perms "$@"
    else
	return $?;
    fi
}

warn () {
    echo "$progname: Warning: $1" >&2
}

# error [exitcode] msg
#
# Print msg (prefixed with progname) to stderr and exit with exitcode
# (default: 1).
error () {
    local exitcode
    exitcode=1
    if [ $# -gt 1 ]; then
	exitcode=$1
	shift
    fi
    safe_echo "$progname: $1" >&2
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

cleanup () {
    if [ "x$tmp_prefix" != "x" ] && [ "x$cleanup_on_exit" != x ]; then
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
    if [ "x$1" = "x--tar-args" ]; then
	_comprcat_tar_args=$2
	shift 2
    fi
    if [ "x$1" = "x--files" ]; then
	_comprcat_tar_args="$_comprcat_tar_args --wildcards $2"
	_comprcat_unzip_args="$2"
	shift 2
    fi
    if [ "x$1" = x ]; then
	cat
    else
	for fname in "$@"; do
	    if [ ! -r "$fname" ]; then
		error "Unable to read input file: $fname"
	    fi
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
		    tar -xaOf "$fname" $_comprcat_tar_args
		    ;;
		*.zip )
		    unzip -p "$fname" $_comprcat_unzip_args
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

# add_prefix prefix [args] ...
#
# Prepend prefix to all args. If no args, do not output anything.
add_prefix () {
    _add_prefix_prefix=$1
    shift
    if [ "$#" != 0 ]; then
	printf -- "$_add_prefix_prefix%s " "$@"
    fi
}

# list_corpora [--registry registry_dir] [--on-error error_cmd] corpus_id ...
#
# List the corpora in the parameters as found in registry_dir
# (default: $cwb_regdir), expanding shell wildcards (but not braces).
# If some listed corpora are not found, call error_cmd (default:
# error) with an error message.
list_corpora () {
    local no_error error_func error_files registry
    no_error=
    error_func=error
    registry=$cwb_regdir
    while [ "x${1##--}" != "x$1" ]; do
	if [ "x$1" = "x--on-error" ]; then
	    error_func=$2
	elif [ "x$1" = "x--registry" ]; then
	    registry=$2
	fi
	shift 2
    done
    ls $(add_prefix $registry/ "$@") \
	2> $tmp_prefix.corpid_errors |
    sed -e 's,.*/,,' |
    grep '^[a-z_][a-z0-9_-]*$' > $tmp_prefix.corpids
    if [ -s $tmp_prefix.corpid_errors ]; then
	error_files=$(
	    sed -e 's,^.*cannot access .*/\([^:/]*\):.*$,\1,' \
		< $tmp_prefix.corpid_errors
	)
	$error_func \
	    "Corpora not found in the CWB corpus registry $registry: $error_files"
    fi
    cat $tmp_prefix.corpids
    rm -rf $tmp_prefix.corpids $tmp_prefix.corpid_errors
}

# run_mysql [--auth | --table table_name] sql_command [MySQL options ...]
#
# Run sql_command on the Korp database using MySQL and get the raw
# output (TSV format; first line containing column names).
#
# If --auth is specified, use the Korp authorization database instead
# of the main database. If --table is specified, use the authorization
# database if table_name begins with "auth_", otherwise the main
# database. Note that this assumes that only the authorization
# database has table names beginning "auth_" and that all the table
# names in the authorization database begin with it.
#
# MySQL username and password may be specified via the environment
# variables KORP_MYSQL_USER and KORP_MYSQL_PASSWORD. Additional MySQL
# options may be specified after sql_command.
run_mysql () {
    local _db
    _db=$korpdb
    if [ "x$mysql_bin" = x ]; then
	warn "MySQL client mysql not found"
	return 1
    fi
    if [ "x$1" = "x--auth" ]; then
	_db=$korpdb_auth
	shift
    elif [ "x$1" = "x--table" ]; then
	shift
	# Test if the table name begins with "auth_"
	if [ "$1" != "${1#auth_}" ]; then
	    _db=$korpdb_auth
	fi
	shift
    fi
    $mysql_bin $mysql_opts --batch --raw --execute "$@" $_db
}

# mysql_table_exists table_name
#
# Return true if table table_name exists in the Korp MySQL database.
# If table_name begins with "auth_", use the authorization database.
mysql_table_exists () {
    local table result
    table=$1
    result=$(run_mysql --table $table "DESCRIBE $table;" 2> /dev/null)
    if [ "x$result" = x ]; then
	return 1
    fi
}

# mysql_list_table_cols table_name
#
# List the column names of the Korp MySQL database table table_name
# (empty if the table does not exist). If table_name begins with
# "auth_", use the authorization database.
mysql_list_table_cols () {
    local table
    table=$1
    run_mysql --table $table "SHOW COLUMNS FROM $table;" 2> /dev/null |
    tail -n+2 |
    cut -d"$tab" -f1
}

# indent [step] < input > output
#
# Indent the input by step spaces (default: 2).
indent_input () {
    if [ "x$1" != x ]; then
	_step=$1
    else
	_step=2
    fi
    _spaces=""
    for i in $(seq $_step); do
	_spaces="$_spaces "
    done
    awk '{print "'"$_spaces"'" $0}'
}

# set_corpus_registry dir
#
# Set the CWB corpus registry directory (CORPUS_REGISTRY, cwb_regdir)
# to dir.
set_corpus_registry () {
    CORPUS_REGISTRY=$1
    export CORPUS_REGISTRY
    corpus_registry_set=1
    cwb_regdir=$CORPUS_REGISTRY
}

# set_corpus_root dir
#
# Set the CWB corpus root directory (corpus_root) to dir and set
# CORPUS_REGISTRY to dir/registry unless already set externally (in
# which case set cwb_regdir to $CORPUS_REGISTRY).
set_corpus_root () {
    corpus_root=$1
    if [ "x$CORPUS_REGISTRY" = x ] || [ "x$corpus_registry_set" != "x" ]; then
	set_corpus_registry "$corpus_root/registry"
    fi
    cwb_regdir=$CORPUS_REGISTRY
}

# _cwb_registry_find_nonexistent_attrs registry_file prefix attrname ...
_cwb_registry_find_nonexistent_attrs () {
    local _regfile _prefix _new_attrs _attrname
    _regfile=$1
    _prefix=$2
    shift 2
    _new_attrs=
    for _attrname in $*; do
	if ! grep -E -q "^$_prefix$_attrname( |\$)" "$_regfile"; then
	    _new_attrs="$_new_attrs $_attrname"
	fi
    done
    echo $_new_attrs
}

# _cwb_registry_make_attrdecls format attrname ...
_cwb_registry_make_attrdecls () {
    local _format _attrname
    _format=$1
    shift
    for _attrname in $*; do
	echo $_attrname;
    done |
    awk '{printf "'"$_format"'\\n", $0}'
}

# cwb_registry_add_posattr corpus attrname ...
#
# Add positional attributes to the CWB registry file for corpus at the
# end of the list of positional attributes if they do not already
# exist. (The function does not use cwb-regedit, because it would
# append the attributes at the very end of the registry file.)
cwb_registry_add_posattr () {
    local _corpus _regfile _new_attrs _new_attrdecls
    _corpus=$1
    shift
    _regfile="$cwb_regdir/$_corpus"
    _new_attrs=$(
	_cwb_registry_find_nonexistent_attrs "$_regfile" "ATTRIBUTE " $*
    )
    _new_attrdecls="$(_cwb_registry_make_attrdecls "ATTRIBUTE %s" $_new_attrs)"
    if [ "x$_new_attrdecls" != "x" ]; then
	cp -p "$_regfile" "$_regfile.old"
	awk '/^ATTRIBUTE/ { prev_attr = 1 }
	     /^$/ && prev_attr { printf "'"$_new_attrdecls"'"; prev_attr = 0 }
	     { print }' "$_regfile.old" > "$_regfile"
    fi
    ensure_perms "$_regfile" "$_regfile.old"
}

# cwb_registry_add_structattr corpus struct [attrname ...]
#
# Add structural attributes (annotations) of the structure struct to
# the CWB registry file for corpus at the end of the list of
# structural attributes if they do not already exist. If attrname are
# not specified, only add struct without annotations. (The function
# does not use cwb-regedit, because it would append the attributes at
# the very end of the registry file.)
cwb_registry_add_structattr () {
    local _corpus _struct _regfile _new_attrs _new_attrs_prefixed
    local _new_attrdecls _xml_attrs
    _corpus=$1
    _struct=$2
    shift 2
    _regfile="$cwb_regdir/$_corpus"
    if ! grep -q "STRUCTURE $_struct\$" "$_regfile"; then
	cp -p "$_regfile" "$_regfile.old"
	awk '/^$/ { empty = empty "\n"; next }
             /^# Yours sincerely/ { printf "\n# <'$_struct'> ... </'$_struct'>\n# (no recursive embedding allowed)\nSTRUCTURE '$_struct'\n" }
             /./ { printf empty; print; empty = "" }' \
		 "$_regfile.old" > "$_regfile"
    fi
    _new_attrs=$(
	_cwb_registry_find_nonexistent_attrs "$_regfile" \
	    "STRUCTURE ${_struct}_" $*
    )
    if [ "x$_new_attrs" != "x" ]; then
	_new_attrs_prefixed=$(
	    echo $_new_attrs |
	    awk '{ for (i = 1; i <= NF; i++) { print "'$_struct'_" $i } }'
	)
	_new_attrdecls="$(
	    _cwb_registry_make_attrdecls "STRUCTURE %-20s # [annotations]" $_new_attrs_prefixed
        )"
	_xml_attrs="$(
	    echo $_new_attrs |
	    awk '{ for (i = 1; i <= NF; i++) { printf " %s=\\\"..\\\"", $i } }'
	)"
	cp -p "$_regfile" "$_regfile.old"
	awk '
	    /^# <'$_struct'[ >]/ { sub(/>/, "'"$_xml_attrs"'>") }
	    /^STRUCTURE '$_struct'(_|$)/ { prev_struct = 1 }
	    /^$/ && prev_struct {
                printf "'"$_new_attrdecls"'";
                prev_struct = 0;
            }
	    { print }' "$_regfile.old" > "$_regfile"
    fi
    ensure_perms "$_regfile" "$_regfile.old"
}

# cwb_index_posattr corpus attrname ...
#
# Index and compress encoded CWB positional attributes attrname in
# corpus (without using cwb-make).
cwb_index_posattr () {
    local _corpus _attrname
    _corpus=$1
    shift
    for _attrname in $*; do
	$cwb_bindir/cwb-makeall -M 2000 $_corpus $_attrname
	$cwb_bindir/cwb-huffcode -P $_attrname $_corpus
	$cwb_bindir/cwb-compress-rdx -P $_attrname $_corpus
	for ext in "" .rdx .rev; do
	    rm "$corpus_root/data/$_corpus/$_attrname.corpus$ext"
	done
    done
}

# corpus_has_attr corpus attrtype attrname
#
# Return true if corpus has attribute attrname of type attrtype (p =
# positional, s = structural, a = alignment).
corpus_has_attr () {
    local corpus attrtype attrname
    corpus=$1
    attrtype=$2
    attrname=$3
    shift 3
    case $attrtype in
	[pP]* )
	    attrtype="ATTRIBUTE"
	    ;;
	[sS]* )
	    attrtype="STRUCTURE"
	    ;;
	[aA]* )
	    attrtype="ALIGNED"
	    ;;
	* )
	    return 1
	    ;;
    esac
    grep -E -q -s "^$attrtype +$attrname\b" $cwb_regdir/$corpus
}

# corpus_exists corpus
#
# Return true if corpus exists (cwb-describe-corpus returns true).
corpus_exists () {
    $cwb_bindir/cwb-describe-corpus $1 > /dev/null 2> /dev/null
}

# get_corpus_token_count corpus
#
# Print the number of tokens in corpus.
get_corpus_token_count () {
    $cwb_bindir/cwb-describe-corpus -s $1 |
    awk '$1 ~ /^size/ {print $3}'
}

# replace_file [--backup backup_file] old_file new_file
#
# Safely replace old_file with new_file. If --backup is specified,
# rename old_file as backup_file.
#
# TODO: Allow numbered backups
replace_file () {
    local oldfile newfile bakfile backup
    backup=
    if [ "x$1" = "x--backup" ]; then
	backup=1
	bakfile=$2
	shift 2
    fi
    oldfile=$1
    newfile=$2
    if [ "x$bakfile" = x ]; then
	bakfile=$oldfile.old
    fi
    if [ ! -r "$oldfile" ]; then
	error "Cannot read file: $oldfile"
    fi
    {
	mv -f "$oldfile" "$bakfile" &&
	mv -f "$newfile" "$oldfile"
    }
    if [ "$?" = 0 ]; then
	if [ "x$backup" = x ]; then
	    rm "$bakfile"
	fi
    else
	# If the old file was removed, replace it with the backup file
	if [ ! -e "$oldfile" ] && [ -e "$bakfile" ]; then
	    mv -f "$bakfile" "$oldfile"
	fi
	error "Could not replace file $oldfile with $newfile"
    fi
}

# optinfo_get_sect filename sectname
#
# Output the section sectname in the option information file filename.
optinfo_get_sect () {
    local file sectname
    file=$1
    sectname=$2
    awk "/^-----<<$sectname/,/^----->>/" $file | grep -v '^-----'
}

# optinfo_init < optspecs
#
# Initialize variables containing option processing code based on the
# option specifications read from standard input. Set the following
# variables: optinfo_cmdline_args, optinfo_getopt_opts,
# optinfo_set_defaults, optinfo_opt_usage, optinfo_opt_handler.
optinfo_init () {
    local make_opthandler_opts optinfo_file
    make_opthandler_opts='--_output-section-format -----<<{name}\n{content}\n----->>\n'
    optinfo_file=$tmp_prefix.optinfo
    if [ "x$config_file_optname" != "x" ]; then
	make_opthandler_opts="$make_opthandler_opts --_config-file-option-name $config_file_optname"
    fi
    $scriptdir/shutil-make-optionhandler.py $make_opthandler_opts "$@" \
	> $optinfo_file 2> $tmp_prefix.optparse-errors
    if [ -s $tmp_prefix.optparse-errors ]; then
	error "Error: $(sed -e 's/.* error: //' $tmp_prefix.optparse-errors)"
    fi
    optinfo_cmdline_args="$(optinfo_get_sect $optinfo_file cmdline_args)"
    optinfo_getopt_opts="$(optinfo_get_sect $optinfo_file getopt_opts)"
    optinfo_set_defaults="$(optinfo_get_sect $optinfo_file set_defaults)"
    optinfo_opt_usage="$(optinfo_get_sect $optinfo_file opt_usage)"
    optinfo_opt_handler="$(optinfo_get_sect $optinfo_file opt_handler)"
    # $optinfo_file is removed at cleanup unless cleanup_on_exit is
    # empty
    # rm $optinfo_file
}

# usage
#
# Output a usage message based on the option information generated
# from $optspecs, with $usage_header at the beginning and optionally
# $usage_footer at the end. Exit with code 0.
usage () {
    safe_echo "$usage_header"
    # Expand variable references inside $optinfo_opt_usage but retain
    # spacing.
    [ "x$optinfo_opt_usage" != "x" ] && eval "cat <<OPTS_EOF

Options:
$optinfo_opt_usage
OPTS_EOF"
    [ "x$usage_footer" != "x" ] && safe_echo "
$usage_footer"
    exit 0
}


# in_str substring string
#
# Return true if string contains substring, false otherwise.
#
# http://stackoverflow.com/questions/229551/string-contains-in-bash#20460402
in_str () {
    local substr str
    substr=$1
    str=$2
    [ -z "${str##*$substr*}" ] && [ -z "$substr" -o -n "$str" ]
}

# word_in word text
#
# Return true if text contains word, text words separated by spaces.
word_in () {
    in_str " $1 " " $2 "
}

# word_index word args ...
#
# Output the one-based number of the first argument in args that is
# equal to word; -1 if none is.
word_index () {
    local word arg argnr
    word=$1
    shift
    argnr=1
    for arg in "$@"; do
	if [ "$word" = "$arg" ]; then
	    echo $argnr
	    return
	fi
	argnr=$(($argnr + 1))
    done
    echo -1
}

# count_words args ...
#
# Output the number of arguments.
count_words () {
    echo "$#"
}

# get_attr_num attrname attrlist
#
# Output the one-based number of positional attribute attrname
# (possibly followed by a slash) in attrlist.
get_attr_num () {
    # set -vx
    local attrname attrlist index
    attrname=$1
    attrlist=$2
    index=$(word_index $attrname $attrlist)
    if [ "$index" = -1 ]; then
	index=$(word_index $attrname/ $attrlist)
    fi
    echo $index
    # set +vx
}

# nth_arg n arg ...
#
# Output the argument number n (one-based) of the rest of the
# arguments.
nth_arg () {
    local n
    n=$1
    shift
    eval echo "\${$n}"
}

# is_int arg
#
# Return true if arg is an integer
#
# Source: https://stackoverflow.com/a/309789
is_int () {
    [ "$1" -eq "$1" 2> /dev/null ]
}


# decode_special_chars [--xml-entities]
#
# Decode the special characters encoded in Korp corpora in stdin and
# write to stdout. If --xml-entities is specified, decode < and > as
# &lt; and &gt;.
#
# This is faster than using vrt-convert-chars.py --decode.
decode_special_chars () {
    local lt gt
    lt="<"
    gt=">"
    if [ "x$1" = "x--xml-entities" ]; then
	lt="&lt;"
	gt="&gt;"
    fi
    perl -CSD -pe 's/\x{007f}/ /g; s/\x{0080}/\//g;
                   s/\x{0081}/'"$lt"'/g; s/\x{0082}/'"$gt"'/g;
                   s/\x{0083}/|/g'
}


# Common initialization code

# Original (unprocessed) command line (arguments), shell expansions
# done and without redirections, but options not processed
cmdline_args_orig=$(echo_quoted "$@")
cmdline_orig="$(echo_quoted "$0") $cmdline_args_orig"

# The tab character
tab='	'

# The (main) directory for scripts (also containing this file): needed
# instead of $progdir for scripts in the subdirectories of corp/ to be
# able to run scripts in the main script directory. NOTE that this
# only works for Bash; for sh scripts, you need to set scriptdir
# manually in the main script if it is not the same as $progdir.
if [ "x$scriptdir" = x ]; then
    if [ "x$BASH_VERSION" != x ]; then
	scriptdir=$(dirname "${BASH_SOURCE[0]}")
    else
	scriptdir=$progdir
    fi
fi

default_corpus_roots=${default_corpus_roots:-"/v/corpora /proj/clarin/korp/corpora $WRKDIR/corpora /wrk/jyniemi/corpora"}

# Root directory, relative to which the corpus directory resides
set_corpus_root ${CORPUS_ROOT:-$(find_existing_dir -d "" $default_corpus_roots)}

default_cwb_bindirs=${default_cwb_bindirs:-"/usr/local/cwb/bin /usr/local/bin /proj/clarin/korp/cwb/bin $USERAPPL/bin /v/util/cwb/utils"}

# The directory in which CWB binaries reside
cwb_bindir=${CWB_BINDIR:-$(find_existing_dir -e cwb-describe-corpus $default_cwb_bindirs)}

default_korp_frontend_dirs=${default_korp_frontend_dirs:-"/var/www/html/korp /var/www/html"}

# The (main) Korp frontend directory
korp_frontend_dir=${KORP_FRONTEND_DIR:-$(find_existing_dir -e config.js $default_korp_frontend_dirs)}

default_filegroups="korp clarin"
find_filegroup $default_filegroups

# File permissions used by ensure_perms
fileperms=ug+rwX,o+rX

# Directory for temporary files
tmpdir=${TMPDIR:-${TEMPDIR:-${TMP:-$TEMP}}}
if [ "x$tmpdir" = "x" ]; then
    default_tmpdirs=${default_tmpdirs:-"/tmp /var/tmp"}
    tmpdir_cands=
    # Find the directories that are writable
    for tmpdir_cand in $default_tmpdirs; do
	if [ -w $tmpdir_cand ]; then
	    tmpdir_cands="$tmpdir_cands $tmpdir_cand"
	fi
    done
    # Find the directory with the most free space: first find the
    # number of the dir in $tmpdir_cands, then choose the dir with
    # that number.
    tmpdir_num=$(
	df $tmpdir_cands |
	tail -n+2 |
	cat -n |
	awk '{print $1 "\t" $5}' |
	sort -s -k2,2nr |
	head -1 |
	cut -d"$tab" -f1
    )
    tmpdir=$(echo $tmpdir_cands | cut -d' ' -f$tmpdir_num)
fi
tmp_prefix=$tmpdir/$progname.$$

# Korp MySQL database
korpdb=korp
# Korp MySQL database for authorization
korpdb_auth=korp_auth
# Unless specified via environment variables, assume that the Korp
# MySQL database user and password are specified in a MySQL option
# file
mysql_opts=
if [ "x$KORP_MYSQL_USER" != "x" ]; then
    mysql_opts="$mysql_opts --user=$KORP_MYSQL_USER"
elif [ "x$MYSQL_USER" != "x" ]; then
    mysql_opts="$mysql_opts --user=$MYSQL_USER"
fi
if [ "x$KORP_MYSQL_PASSWORD" != "x" ]; then
    mysql_opts="$mysql_opts --password=$KORP_MYSQL_PASSWORD"
elif [ "x$MYSQL_PASSWORD" != "x" ]; then
    mysql_opts="$mysql_opts --password=$MYSQL_PASSWORD"
fi
if [ "x$KORP_MYSQL_BIN" != "x" ]; then
    mysql_bin=$KORP_MYSQL_BIN
elif [ -x /opt/mariadb/bin/mysql ]; then
    # MariaDB on the Korp server
    mysql_bin="/opt/mariadb/bin/mysql --defaults-extra-file=/var/lib/mariadb/my.cnf"
else
    mysql_bin=$(find_prog mysql)
fi

if [ "x$debug" != x ]; then
    cleanup_on_exit=
else
    cleanup_on_exit=1
fi

show_times=


trap cleanup 0
trap cleanup_abort 1 2 13 15


# If the variable optspecs has been defined, initialize option
# processing code based on it.
if [ "x$optspecs" != x ]; then
    # We cannot use a pipe here, since optinfo_init would be run in a
    # different process and the variables set in it would not be
    # visible after the call.
    safe_echo "$optspecs" > $tmp_prefix.optspecs
    optinfo_init "$@" < $tmp_prefix.optspecs
    eval "$optinfo_getopt_opts"
    eval "$optinfo_set_defaults"
    eval set -- "$optinfo_cmdline_args"
fi

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

# Command line (arguments) with options processed
cmdline_args_processed=$(echo_quoted "$@")
cmdline_processed="$(echo_quoted "$0") $cmdline_args_processed"
