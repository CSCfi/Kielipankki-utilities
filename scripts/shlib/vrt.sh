# -*- coding: utf-8 -*-

# shlib/vrt.sh
#
# Library functions for Bourne shell scripts: functions for VRT files
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# Load shlib components for the functions used
shlib_required_libs="file msgs"
. $_shlibdir/loadlibs.sh


# Public functions

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


# vrt_decode_special_chars [--xml-entities | --no-xml-entities]
#
# Decode the special characters encoded in the Korp corpora of the
# Language Bank of Finland in stdin and write to stdout. If
# --no-xml-entities is specified, keep < and > literally (e.g., for
# database data) instead of encoding them as &lt; and &gt; (for VRT)
# and also decode &amp;, &quot; and &apos;. --xml-entities is the
# default.
#
# Despite the name of the function, it can be used to decode CWB data
# (attribute values) in addition to VRT.
#
# With --xml-entities (the default), this is somewhat faster than
# using vrt-convert-chars.py --decode.
vrt_decode_special_chars () {
    local perl_subst
    perl_subst=$_perl_decode_special_chars_xml
    if [ "x$1" = "x--no-xml-entities" ]; then
	perl_subst=$_perl_decode_special_chars_literal
    elif [ "x$1" != x ] && [ "x$1" != "x--xml-entities" ]; then
	lib_error "vrt_decode_special_chars: Invalid option or argument: $1"
    fi
    perl -CSD -pe "$perl_subst"
}


# set_xml_char_entity_map mapping
#
# Use mapping as the XML character entity map. mapping has lines in
# the format "source target" where source is the Perl regular
# expression to substitute with target. Spaces and quotation marks
# should be expressed via character codes.
set_xml_char_entity_map () {
    xml_char_entity_map=$1
    _initialize_perl_substs
}

# set_special_char_map mapping
#
# Use mapping as the encoded special characters map. mapping has lines
# in the format "source target" where source is the Perl regular
# expression to substitute with target. Spaces and quotation marks
# should be expressed via character codes.
set_special_char_map () {
    special_char_map=$1
    _initialize_perl_substs
}


# Private functions

# _convert_mapping_to_perl_substs [mapping]
#
# Output Perl code to substitute strings based on mapping, which has
# lines in the format "source target" where source is the Perl regular
# expression to substitute with target. Spaces and quotation marks
# should be expressed via character codes. If mapping is not specified
# as an argument, it is read from stdin.
_convert_mapping_to_perl_substs () {
    local get_mapping
    if [ "x$1" != x ]; then
	get_mapping="printf %s \"$1\""
    else
	get_mapping=cat
    fi
    eval "$get_mapping" |
	perl -pe 's!(\S+)\s+(\S+)!s,$1,$2,g;!g'
}

# _initialize_perl_substs
#
# Initialize the variables containing Perl substitutions for XML
# character entities and encoded special characters:
# - _perl_subst_xml_entities: substitute XML character entities with
#    the corresponding literal characters
# - _perl_decode_special_chars_xml: decode encoded special characters;
#    output &lt; and &gt; for < and >
# - _perl_decode_special_chars_literal: decode encoded special
#    characters; output < and > literally and also convert other XML
#    character entities to literal characters
_initialize_perl_substs () {
    if [ "x$xml_char_entity_map" != x ]; then
	_perl_subst_xml_entities=$(
	    _convert_mapping_to_perl_substs "$xml_char_entity_map")
    fi
    if [ "x$special_char_map" != x ]; then
	_perl_decode_special_chars_xml=$(
	    _convert_mapping_to_perl_substs "$special_char_map")
	_perl_decode_special_chars_literal=$(
	    {
		printf %s "$special_char_map" |
		    perl -CSD -pe "$_perl_subst_xml_entities"
		# Exclude from $xml_char_entity_map the lines
		# containing strings present in $special_char_map
		echo "$xml_char_entity_map" |
		    grep -Fv "$(echo $special_char_map | tr ' ' '\n')"
	    } |
		_convert_mapping_to_perl_substs
					  )
    fi
}


# Initialize variables

# XML character entities to decode
set_xml_char_entity_map '
    &lt; <
    &gt; >
    &amp; &
    &quot; \x22
    &apos; \x27
'

# Special characters to decode
set_special_char_map '
    \x{007f} \x20
    \x{0080} /
    \x{0081} &lt;
    \x{0082} &gt;
    \x{0083} |
'
