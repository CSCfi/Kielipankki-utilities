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
# Output all args with prefix prepended to each, separated by a space.
# If no args, do not output anything.
add_prefix () {
    local prefix result
    prefix=$1
    shift
    if [ "$#" != 0 ]; then
        result=$(printf -- "$prefix%s " "$@")
        # Remove trailing space
        safe_echo "${result% }"
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

# str_hasprefix string prefix
#
# Returns true if string starts with prefix, false otherwise.
str_hasprefix () {
    local str prefix
    str=$1
    prefix=$2
    [ -z "${str##$prefix*}" ] && [ -z "$prefix" -o -n "$str" ]
}

# str_hassuffix string suffix
#
# Returns true if string ends with suffix, false otherwise.
str_hassuffix () {
    local str suffix
    str=$1
    suffix=$2
    [ -z "${str%%*$suffix}" ] && [ -z "$suffix" -o -n "$str" ]
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

# suffix_word wordlist word suffix
#
# Output wordlist with each occurrence of word (matching as a whole)
# suffixed with suffix. Words in wordlist are separated by spaces, but
# word and suffix may also contain spaces, so the function can be used
# to add words following the given words.
#
# Requires Bash because of using ${.../.../...}
suffix_word () {
    local wordlist word suffix
    # Add a space at the beginning and end so that a suffix can be
    # added to the first and last word
    wordlist=" $1 "
    word=$2
    suffix=$3
    wordlist=${wordlist//" $word "/" $word$suffix "}
    # Remove the extra space at the beginning and end
    wordlist=${wordlist% }
    wordlist=${wordlist# }
    safe_echo "$wordlist"
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


# but_n_first_args n arg ...
#
# Output the arguments (starting from the second argument) except for
# the n first ones. Note that the output loses the distinction between
# spaces between and within arguments.
but_n_first_args () {
    local n
    n=$1
    shift
    shift $n
    echo "$@"
}


# is_int arg
#
# Return true if arg is an integer
#
# Source: https://stackoverflow.com/a/309789
is_int () {
    [ "$1" -eq "$1" 2> /dev/null ]
}


# foreach_filter filter_code foreach_code item ...
#
# Eval foreach_code for each item for which eval'ed filter_code
# returns true. For both filter_code and foreach_code, $item is set to
# the item and $itemnum to its index (one-based). If filter_code is an
# empty string, use the default 'true'. If foreach_code is an empty
# string, use the default 'safe_echo "$item"'.
foreach_filter () {
    local filter_code foreach_code item itemnum
    filter_code=$1
    foreach_code=$2
    shift
    shift
    if [ "x$filter_code" = x ]; then
	filter_code=true
    fi
    if [ "x$foreach_code" = x ]; then
	foreach_code='safe_echo "$item"'
    fi
    itemnum=1
    for item in "$@"; do
	if eval "$filter_code"; then
	    eval "$foreach_code"
	fi
	itemnum=$(($itemnum + 1))
    done
}


# delimit delimiter [item ...]
#
# Output items delimited by delimiter. The output has no newline at
# the end (unless the last item ends in a newline).
delimit () {
    local sep
    sep=$1
    shift
    while [ $# -gt 1 ]; do
        printf "%s" "$1$sep"
        shift
    done
    printf "$1"
}


# strsplit delimiter str
#
# Output str split at delimiter, each item on a separate line.
strsplit () {
    local sep first rest
    sep=$1
    rest=$2
    while true; do
        first=${rest%%$sep*}
        printf "%s\n" "$first"
        rest=${rest#*$sep}
        if [ "$rest" = "$first" ]; then
            break
        fi
    done
}


# integer number
#
# Output the integer part of number.
integer () {
    local num
    num=$1
    echo ${num%.*}
}


# semver_ge version_str major [minor [patch]]
#
# Return true if the version specified by the semantic version string
# version_str ("major.minor.patch") is greater than or equal to the
# version specified by major, minor and patch; false otherwise. If
# patch or minor is omitted, it is assumed to be 0.
semver_ge () {
    local version major minor patch comp
    version=$1
    major=$2
    minor=$3
    patch=$4
    [ "$minor" = "" ] &&
        minor=0
    [ "$patch" = "" ] &&
        patch=0
    # Major
    comp=${version%%.*}
    [ $comp -gt $major ] &&
        return 0
    [ $comp -lt $major ] &&
        return 1
    # Minor
    version=${version#*.}
    comp=${version%%.*}
    { [ "$comp" = "" ] || [ $comp -gt $minor ]; } &&
        return 0
    [ $comp -lt $minor ] &&
        return 1
    # Patch
    comp=${version#*.}
    { [ "$comp" = "" ] || [ $comp -gt $patch ]; } &&
        return 0
    [ $comp -lt $patch ] &&
        return 1
    return 0
}
