#! /bin/sh
# -*- coding: utf-8 -*-

# Usage: vrt-add-struct-ids.sh [options] [input.vrt ...] > output.vrt


progname=`basename $0`
progdir=`dirname $0`


usage_header="Usage: $progname [options] [input.vrt ...] > output.vrt

Add (or replace) id attributes to the specified structural attributes
(elements) of the input VRT."

optspecs='
structure|element=STRUCT[:FORMAT] * structspecs
    add (or replace if --force is specified) an id attribute to the
    structure STRUCT based on the number of STRUCT counted from the
    beginning of the input, formatted using the printf-style format
    string FORMAT; if :FORMAT is omitted, use the default format "%d"
    (a plain number); this option must be specified at least once and
    may be repeated
id-attribute-name=ATTRNAME "id" id_attrname
    use ATTRNAME as the id attribute name
force
    overwrite possibly existing id attributes in the specified
    structures; the default is to preserve them
'

. $progdir/korp-lib.sh

# Process options
eval "$optinfo_opt_handler"


if [ "x$structspecs" = "x" ]; then
    error "Please specify at least one structure with --structure"
fi


make_add_ids_code () {
    local spec struct subst
    add_ids_code=
    for spec in $structspecs; do
	struct=${spec%%:*}
	if [ "x$struct" = "x$spec" ]; then
	    subst="\" $id_attrname=\\\"\$$struct\\\"\""
	else
	    subst="sprintf ' $id_attrname=\"${spec#*:}\"', \$$struct"
	fi
	add_ids_code="$add_ids_code
if (/^<${struct}[\s>]/) {
    \$$struct++;
    if (! / $id_attrname=\"/) {
        s/^(<${struct})([\s>])/\$1 . ($subst) . \$2/e;
    }"
	if [ "x$force" != x ]; then
	    add_ids_code="$add_ids_code else {
        s/ $id_attrname=\".*?\"/$subst/e;
    }"
	fi
	add_ids_code="$add_ids_code
}"
    done
    echo_dbg "$add_ids_code"
}

add_ids () {
    make_add_ids_code
    perl -pe "$add_ids_code"
}


comprcat --files "*.vrt" "$@" |
add_ids
