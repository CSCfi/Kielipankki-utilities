#! /bin/sh
# -*- coding: utf-8 -*-

# TODO (many of these would require support in shlib/cwb.sh):
# - Allow shell wildcards or regular expressions in attribute names.
# - Support soft removal by commenting out an attribute name in the
#   registry.


progname=$(basename $0)
progdir=$(dirname $0)

usage_header="Usage: $progname [options] command attrnamelist corpus ...

Manage (copy, rename, alias or remove) the specified attributes from
the specified CWB corpora. Affects both the corpus registry file and
the data files.

command is one of copy (= cp), rename (mv), alias (link, ln) or remove
(rm).

attrnamelist is the list of (pairs of) names of attributes to manage,
separated by spaces. If a bare structure name is specified, all its
attributes with annotations are also processed. For copy, rename and
alias, the attribute names are pairs SOURCE:TARGET, where SOURCE is
the original attribute name and TARGET the new one.

Corpus ids may contain shell wildcards."

optspecs='
force
    Force overwriting an existing target attribute with copy, rename
    or alias. The existing data files are backed up by default; use
    --backup-suffix="" to omit backups.
backup-suffix|suffix=SUFFIX "__DEFAULT" baksuff
    Use SUFFIX instead of .bak-YYYYMMDDhhmmss as the suffix for the
    backups of the registry file and possible existing destination
    data files; use "" to make no backups.
comment=COMMENT "__DEFAULT"
    Add comment COMMENT to the registry file instead of a standard
    comment describing the change; use "" to omit the comment.
quiet !verbose
    Suppress informational and warning messages.
'


. $progdir/korp-lib.sh


# Process options
eval "$optinfo_opt_handler"


case "$1" in
    "copy" | "cp" )
	command="copy"
	cmd_verb="copied"
	;;
    "rename" | "mv" )
	command="rename"
	cmd_verb="renamed"
	;;
    "alias" | "link" | "ln" )
	command="alias"
	cmd_verb="aliased"
	;;
    "remove" | "rm" )
	command="remove"
	cmd_verb="removed"
	;;
    "" )
	error "Please specify command, attribute name list and at least one corpus"
	;;
    * )
	error "Unrecognized command \"$1\""
	;;
esac
if [ "x$2" = x ]; then
    error "Please specify attribute name list and at least one corpus"
elif [ "x$3" = x ]; then
    error "Please specify at least one corpus"
fi

attrnames_orig=$2
shift 2

attrnames=
if [ $command != "remove" ]; then
    for attrname in $attrnames_orig; do
	if ! in_str ":" $attrname; then
	    verbose warn "Attribute specifications for $command must of the form \"source:target\"; skipping \"$attrname\""
	elif [ "${attrname%:*}" = "${attrname#*:}" ]; then
	    verbose warn "Source and target attribute cannot be the same; skipping \"$attrname\""
	else
	    attrnames="$attrnames $attrname"
	fi
    done
else
    attrnames=$attrnames_orig
fi

corpora=$(list_corpora "$@")


attr_is_valid () {
    local corpus attrname_src attrname_dst attrtype_src attrtype_dst
    corpus=$1
    attrname_src=$2
    attrname_dst=$3
    attrtype_src=$(corpus_get_attr_type_full $corpus $attrname_src)
    if [ "x$attrtype_src" = x ]; then
	verbose warn "Corpus $corpus has no attribute $attrname_src"
	return 1
    elif [ $command != "remove" ]; then
	attrtype_dst=$(corpus_get_attr_type_full $corpus $attrname_dst)
	# If the destination attribute already exists, it needs to have
	# the same type as the source.
	if [ "x$attrtype_dst" != x ] && [ "$attrtype_src" != "$attrtype_dst" ]
	then
	    verbose warn "Corpus $corpus: target attribute $attrname_dst already exists but has different type from $attrname_src; skipping"
	    return 1
	fi
	# If the destination attribute does not exist, and if the source
	# attribute is structural with annotations, the destination name
	# must contain an underscore, or if the source is bare structure,
	# the destination name must not contain underscore.
	if [ "x$attrtype_dst" = x ]; then
	    if [ "$attrtype_src" = "s_" ] && ! in_str "_" "$attrname_dst"; then
		verbose warn "Corpus $corpus: source attribute $attrname_src has annotations but target attribute name $attrname_dst has no underscore; skipping"
		return 1
	    elif [ "$attrtype_src" = "s" ] && in_str "_" "$attrname_dst"; then
		verbose warn "Corpus $corpus: source attribute $attrname_src is structural without annotations but target attribute name $attrname_dst has an underscore; skipping"
		return 1
	    fi
	fi
	# If the source attribute is structural with annotations, the bare
	# structure of the destination needs to be the same
	if [ "$attrtype_src" = "s_" ] &&
	       [ "${attrname_src%%_*}" != "${attrname_dst%%_*}" ]
	then
	    verbose warn "Corpus $corpus: source attribute $attrname_src and target $attrname_dst have different structures; skipping"
	    return 1
	fi
    fi
}

manage_attr () {
    local corpus attrname attrname_src attrname_dst attrtype_src attrtype_dst \
	  backup_text all_attrs opts
    corpus=$1
    attrname=$2
    attrname_src=${attrname%:*}
    attrname_dst=${attrname#*:}
    if attr_is_valid $corpus $attrname_src $attrname_dst; then
	if [ $command = "remove" ]; then
	    attrname_dst=
	else
	    attrtype_dst=$(corpus_get_attr_type_full $corpus $attrname_dst)
	    if [ "x$attrtype_dst" != x ]; then
		backup_text="without backups"
		if [ "x$baksuff" != x ]; then
		    backup_text="after backing it up"
		fi
		if [ "x$force" != x ]; then
		    verbose warn "Corpus $corpus: overwriting existing target attribute $attrname_dst ($backup_text) as --force was specified"
		else
		    verbose warn "Corpus $corpus: target attribute $attrname_dst exists; skipping (use --force to overwrite)"
		    return
		fi
	    fi
	fi
	attrtype_src=$(corpus_get_attr_type_full $corpus $attrname_src)
	if [ "x$verbose" != x ]; then
	    if [ "$attrtype_src" = "s" ]; then
		all_attrs=$(corpus_list_attrs $corpus s "$attrname_src(|_.*)")
	    else
		all_attrs=$attrname_src
	    fi
	fi
	opts=""
	if [ "$baksuff" != "__DEFAULT" ]; then
	    opts="--backup-suffix '$baksuff'"
	fi
	if [ "$comment" != "__DEFAULT" ]; then
	    opts="$opts --comment '$comment'"
	fi
	# Use eval to be able to preserve spaces in comment
	# eval echo "corpus_${command}_attr \"$opts\" $corpus $attrname_src $attrname_dst"
	eval corpus_${command}_attr "$opts" $corpus $attrname_src $attrname_dst
	if [ "x$verbose" != x ]; then
	    for attrname in $all_attrs; do
		echo "Corpus $corpus: $cmd_verb attribute $attrname"
	    done
	fi
    fi
}


for corpus in $corpora; do
    for attrname in $attrnames; do
	manage_attr $corpus $attrname
    done
done
