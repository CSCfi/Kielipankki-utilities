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

# For getopt, called in korp-lib.sh
shortopts=hc:r:
longopts=help,corpus-root:,registry:

. $progdir/korp-lib.sh

cwb_regdir=${CORPUS_REGISTRY:-$corpus_root/registry}


usage () {
    cat <<EOF
Usage: $progname [options] source target

Copy a Korp corpus with id "source" to id "target": CWB data directory,
registry file, Korp MySQL data (timespans, lemgram_index, relations tables).

Options:
  -h, --help      show this help
  -c, --corpus-root DIR
                  use DIR as the root directory of corpus files (default:
                  $corpus_root)
  -r, --registry DIR
                  use DIR as the CWB registry (default: $cwb_regdir)
EOF
    exit 0
}


# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	-c | --corpus-root )
	    corpus_root=$2
	    shift
	    ;;
	-r | registry )
	    cwb_regdir=$2
	    shift
	    ;;
	-- )
	    shift
	    break
	    ;;
	--* )
	    warn "Unrecognized option: $1"
	    ;;
	* )
	    break
	    ;;
    esac
    shift
done


extract_datadir () {
    regfile=$1
    grep '^HOME ' $regfile |
    cut -d' ' -f2
}

copy_data () {
    source=$1
    target=$2
    source_datadir=$(extract_datadir $cwb_regdir/$source)
    top_datadir=$(echo "$source_datadir" | sed -e 's,\(.*\)/.*,\1,')
    target_datadir=$top_datadir/$target
    cp -dpr $source_datadir $target_datadir
    ensure_perms $target_datadir
}

copy_registry () {
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
}

mysql_make_copy_table_rows () {
    echo "
INSERT INTO timespans (corpus, datefrom, dateto, tokens)
  SELECT '$target_u', ts.datefrom, ts.dateto, ts.tokens
  FROM timespans AS ts
  WHERE ts.corpus='$source_u';
INSERT INTO lemgram_index (lemgram, freq, freq_prefix, freq_suffix, corpus)
  SELECT li.lemgram, li.freq, li.freq_prefix, li.freq_suffix, '$target_u'
  FROM lemgram_index as li
  WHERE li.corpus='$source_u';
INSERT INTO corpus_info (corpus, "'`key`'", value)
  SELECT '$target_u', ci."'`key`'", ci.value
  FROM corpus_info as ci
  WHERE ci.corpus='$source_u';
"
}

mysql_make_copy_rel_tables () {
    source_u=$1
    target_u=$2
    for tabletype in "" _dep_rel _head_rel _rel _sentences _strings; do
	source_table=relations_$source_u$tabletype
	target_table=relations_$target_u$tabletype
	echo "CREATE TABLE $target_table LIKE $source_table;"
	echo "INSERT INTO $target_table SELECT * FROM $source_table;"
    done
}

copy_database () {
    source=$1
    target=$2
    source_u=$(toupper $source)
    target_u=$(toupper $target)
    {
	mysql_make_copy_table_rows
	mysql_make_copy_rel_tables $source_u $target_u
    } |
    mysql --batch $mysql_opts $korpdb
}

copy_corpus () {
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
