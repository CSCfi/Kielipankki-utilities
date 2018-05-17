# -*- coding: utf-8 -*-

# shlib/str.sh
#
# Generic library functions for Bourne shell scripts: string
# processing
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# Functions

toupper () {
    echo "$1" |
    sed -e 's/\(.*\)/\U\1\E/'
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
