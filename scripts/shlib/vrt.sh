# -*- coding: utf-8 -*-

# shlib/vrt.sh
#
# Library functions for Bourne shell scripts: functions for VRT files
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# Load shlib components for the functions used
shlib_required_libs="file"
. $_shlibdir/loadlibs.sh


# vrt_get_token_count [vrt_file ...]
#
# Print the number of tokens in the VRT input vrt_file. vrt_file may
# be compressed. If vrt_file is not specified, read from stdin.
vrt_get_token_count () {
    comprcat "$@" |
    grep -E -cv '^($|<)'
}

# vrt_get_struct_count struct [vrt_file ...]
#
# Print the number of structures struct in the VRT input vrt_file.
# vrt_file may be compressed. If vrt_file is not specified, read from
# stdin.
vrt_get_struct_count () {
    local struct
    struct=$1
    shift
    comprcat "$@" |
    grep -c "^<$struct "
}


# vrt_get_posattr_names [vrt_file]
#
# Print the positional attribute names in the positional attributes
# comment of vrt_file on a single line, separated by spaces. vrt_file
# may be compressed. If vrt_file is not specified, read from stdin. If
# the input does not contain a positional attributes comment, print
# nothing.
vrt_get_posattr_names () {
    comprcat "$@" |
	perl -ne '
	    if (/^<!--\s*(#vrt\spositional-attributes|Positional attributes):\s*(.*?)\s*-->/) {
	        print "$2\n";
	    } elsif (/^[^<]/) {
	        exit;
            }'
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
