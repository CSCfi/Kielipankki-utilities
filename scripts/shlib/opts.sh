# -*- coding: utf-8 -*-

# shlib/opts.sh
#
# Generic library functions (and initialization code) for Bourne shell
# scripts: option processing
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# Load shlib components for the functions used
shlib_required_libs="base msgs"
. $_shlibdir/loadlibs.sh


# Functions

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
    # Should shutil-make-optionhandler.py be moved to the shlib
    # directory?
    $_shlibdir/../shutil-make-optionhandler.py $make_opthandler_opts "$@" \
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


# Initialize variables

# Original (unprocessed) command line (arguments), shell expansions
# done and without redirections, but options not processed
cmdline_args_orig=$(echo_quoted "$@")
cmdline_orig="$(echo_quoted "$0") $cmdline_args_orig"

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
