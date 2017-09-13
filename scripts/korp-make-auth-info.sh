#! /bin/bash
# -*- coding: utf-8 -*-

progname=`basename $0`
progdir=`dirname $0`


usage_header="Usage: $progname [options] corpus_id ...

Generate authorization information for the specified corpora and optionally
import it to the Korp authorization database. corpus_id may contain shell
wildcards, in which case all matching corpora in the corpus registry are
included."

optspecs='
licence-type=LIC
    the corpus licence type is LIC, where LIC is one of PUB, ACA,
    ACA-Fi or RES
lbr-id=URN
    the LBR id of the corpus is URN of the form
    [$urn_prefix]YYYYMMNNN[@LBR], where YYYYMM is year and month and
    NNN 3 to 5 digits; the bracketed parts are added if left out
tsv-dir=DIRTEMPL "$corpus_root/vrt/{corpid}"
    use DIRTEMPL as the directory template for the generated TSV data
    files; DIRTEMPL is a directory name possibly containing the
    placeholder {corpid} for corpus id
import-database
    import the licence information to the Korp authorization database
v|verbose
    show the names of the generated files
'

. $progdir/korp-lib.sh

# Process options
eval "$optinfo_opt_handler"


check_args () {
    if [ "x$1" = "x" ]; then
	error "No corpus id specified"
    fi
    if [ "x$licence_type$lbr_id" = "x" ]; then
	error "Please specify either --licence-type or --lbr-id or both."
    fi
    if [ "x$licence_type" != "x" ]; then
	licence_type=$(make_licence_type $licence_type)
	exit_if_error $?
    fi
    if [ "x$lbr_id" != "x" ]; then
	lbr_id=$(make_lbr_id $lbr_id)
	exit_if_error $?
    fi
}

make_filename () {
    local corpus table
    corpus=$1
    table=$2
    dirname=$(echo "$tsv_dir" | sed -e "s,{corpid},$corpus,g")
    if [ ! -d "$dirname" ]; then
	exit_on_error mkdir_perms "$dirname"
    fi
    safe_echo "$dirname/${corpus}_auth_$table.tsv"
}

import_database () {
    local filename
    filename=$1
    $progdir/korp-mysql-import.sh --prepare-tables "$filename"
}

make_tsv_file () {
    local corpus table content filename
    corpus=$1
    table=$2
    shift 2
    dirname=$(echo "$tsv_dir" | sed -e "s,{corpid},$corpus,g")
    filename="$(make_filename $corpus $table)"
    exit_if_error $?
    content=$(printf "%s\t" "$@")
    verbose safe_echo "$filename"
    printf "%s\n" "${content%"$tab"}" > "$filename"
    if [ "x$import_database" != "x" ]; then
	import_database "$filename"
    fi
}

main () {
    local corpora corpus
    check_args "$@"
    corpora=$(list_corpora "$@")
    for corpus in $corpora; do
	if [ "x$licence_type" != "x" ]; then
	    verbose printf "Generating licence data file for $corpus: "
	    make_tsv_file $corpus license $corpus "$licence_type"
	fi
	if [ "x$lbr_id" != "x" ]; then
	    verbose printf "Generating LBR map data file for $corpus: "
	    make_tsv_file $corpus lbr_map "$lbr_id" $corpus
	fi
    done
}


main "$@"
