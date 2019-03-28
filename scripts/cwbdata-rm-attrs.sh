#! /bin/sh
# -*- coding: utf-8 -*-

# TODO:
# - Allow shell wildcards or regular expressions in attribute names.


progname=$(basename $0)
progdir=$(dirname $0)

usage_header="Usage: $progname [options] corpus ...

Remove the specified attributes from the specified CWB corpora. Removes the
attributes from the corpus registry file and their data files.

Corpus ids may contain shell wildcards."

optspecs='
attribute-names|attrs=ATTRNAMELIST attrnames
    Remove the attributes listed in ATTRNAMELIST, separated by spaces.
    If a bare structure name is specified, it is removed along with
    all its attributes with annotations.
'


. $progdir/korp-lib.sh


# Process options
eval "$optinfo_opt_handler"


if [ "x$1" = x ]; then
    error "Please specify at least one corpus"
fi
if [ "x$attrnames" = x ]; then
    error "Please specify --attribute-names with at least one attribute name"
fi

corpora=$(list_corpora "$@")

for corpus in $corpora; do
    for attr in $attrnames; do
	attrtype=$(corpus_get_attr_type $corpus $attr)
	if [ "x$attrtype" = x ]; then
	    warn "Corpus $corpus has no attribute $attr"
	else
	    all_attrs=$attr
	    if [ $attrtype = "s" ] && ! in_str _ $attr; then
		all_attrs=$(corpus_list_attrs $corpus s "$attr(|_.*)")
	    fi
	    corpus_remove_attrs $corpus $attr
	    for attr in $all_attrs; do
		echo "Corpus $corpus: removed attribute $attr"
	    done
	fi
    done
done
