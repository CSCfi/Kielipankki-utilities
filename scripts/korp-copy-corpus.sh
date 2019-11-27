#! /bin/sh
# -*- coding: utf-8 -*-

# Copy a Korp corpus to another name: CWB data directory, registry
# file, data in the Korp MySQL database
#
# korp-copy-corpus.sh --help for more information
#
# TODO:
# - An option to copy multiple corpora (possibly using shell
#   wildcards) with copies named using a substitution pattern (sed or
#   Perl).


progname=`basename $0`
progdir=`dirname $0`


usage_header="Usage: $progname [options] source target

Copy a Korp corpus with id \"source\" to id \"target\": CWB data directory,
registry file and Korp MySQL data (time data, lemgram index, relations tables
and authorization data)."

optspecs='
c|corpus-root=DIR "$corpus_root" { set_corpus_root "$1" }
    use DIR as the root directory of corpus files
r|registry=DIR "$cwb_regdir" { set_corpus_registry "$1" }
    use DIR as the CWB registry
'

. $progdir/korp-lib.sh

# Process options
eval "$optinfo_opt_handler"


multicorpus_tables="timedata timedata_date timespans lemgram_index corpus_info"
multicorpus_tables_auth="auth_license auth_lbr_map auth_allow"


extract_datadir () {
    local regfile
    regfile=$1
    grep '^HOME ' $regfile |
    cut -d' ' -f2
}

copy_data () {
    local source target source_datadir top_datadir target_datadir
    source=$1
    target=$2
    source_datadir=$(extract_datadir $cwb_regdir/$source)
    top_datadir=$(echo "$source_datadir" | sed -e 's,\(.*\)/.*,\1,')
    target_datadir=$top_datadir/$target
    cp -dpr $source_datadir $target_datadir
    ensure_perms $target_datadir
}

copy_registry () {
    local source target source_u target_u
    source=$1
    target=$2
    source_u=$(toupper $source)
    target_u=$(toupper $target)
    cat "$cwb_regdir/$source" |
    sed -e '
s,^\(## registry entry for corpus \)'$source_u',\1'$target_u',;
s,^\(ID *\)'$source',\1'$target',;
s,^\(HOME .*/\)'$source',\1'$target',;
s,^\(INFO .*/\)'$source'\(/\.info\),\1'$target'\2,' \
    > "$cwb_regdir/$target"
    ensure_perms "$cwb_regdir/$target"
}

mysql_make_copy_table_rows () {
    local source_u target_u cols cols_list table
    source_u=$1
    target_u=$2
    shift
    shift
    for table in "$@"; do
	cols=$(mysql_list_table_cols $table)
	if [ "x$cols" != x ]; then
	    cols_list=$(
		echo $cols |
		sed -e 's/\([^ ][^ ]*\)/`\1`/g; s/ /, /g;
                        s/`corpus`/'"'$target_u'/"
	    )
	    echo "INSERT IGNORE INTO $table
                  SELECT $cols_list FROM $table where corpus='$source_u';"
	fi
    done
}

mysql_make_copy_rel_tables () {
    local source_u target_u tabletype source_table target_table
    source_u=$1
    target_u=$2
    for tabletype in "" _dep_rel _head_rel _rel _sentences _strings; do
	source_table=relations_$source_u$tabletype
	target_table=relations_$target_u$tabletype
	if mysql_table_exists $source_table; then
	    echo "CREATE TABLE IF NOT EXISTS $target_table LIKE $source_table;"
	    echo "INSERT IGNORE INTO $target_table SELECT * FROM $source_table;"
	fi
    done
}

copy_database () {
    local source target source_u target_u
    source=$1
    target=$2
    source_u=$(toupper $source)
    target_u=$(toupper $target)
    {
	mysql_make_copy_table_rows $source_u $target_u $multicorpus_tables
	mysql_make_copy_rel_tables $source_u $target_u
    } |
	run_mysql
    mysql_make_copy_table_rows $source_u $target_u $multicorpus_tables_auth |
	run_mysql --auth
}

copy_corpus () {
    local source target
    source=$1
    target=$2
    test "x$target" != "x" ||
    error "Usage: $progname [options] source target
$progname --help for more information"
    test -e "$cwb_regdir/$source" ||
    error "Corpus $source not found in registry $cwb_regdir"
    test ! -e "$cwb_regdir/$target" ||
    error "Corpus $target is already in the registry; not overwriting"
    copy_data $source $target
    copy_registry $source $target
    copy_database $source $target
}


copy_corpus $1 $2
