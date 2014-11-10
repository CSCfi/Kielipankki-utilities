#! /bin/sh
# -*- coding: utf-8 -*-

# Usage: korp-mysql-import.sh [options] filename ...
#
# For more information, run korp-mysql-import.sh --help

# TODO:
# - Optionally do not import already imported files (listed in a list file)
# - Optionally log MySQL errors and import times


progname=`basename $0`

tmpdir=${TMPDIR:-${TEMPDIR:-${TMP:-${TEMP:-/tmp}}}}
tmpfname_base=$tmpdir/$progname.$$.tmp

dbname=korp

prepare_tables=

table_columns_lemgram_index='
	`lemgram` varchar(64) NOT NULL,
	`freq` int(11) DEFAULT NULL,
	`freqprefix` int(11) DEFAULT NULL,
	`freqsuffix` int(11) DEFAULT NULL,
	`corpus` varchar(64) NOT NULL,
	UNIQUE KEY `lemgram_corpus` (`lemgram`, `corpus`),
	KEY `lemgram` (`lemgram`),
	KEY `corpus` (`corpus`)
'
table_columns_timespans='
	`corpus` varchar(64) NOT NULL,
	`datefrom` varchar(14) DEFAULT '"''"',
	`dateto` varchar(14) DEFAULT '"''"',
	`tokens` int(11) DEFAULT 0,
	KEY `corpus` (`corpus`)
'
table_columns_relations_CORPNAME='
        `id` int(11) UNIQUE NOT NULL,
	`head` varchar(100) NOT NULL,
	`rel` char(3) NOT NULL,
	`dep` varchar(100) NOT NULL,
	`depextra` varchar(32) DEFAULT NULL,
	`freq` int(11) NOT NULL,
	`wf` tinyint(4) NOT NULL,
	PRIMARY KEY (`id`),
	KEY `head` (`head`),
	KEY `dep` (`dep`)
'
table_columns_relations_CORPNAME_rel='
	`rel` char(3) NOT NULL,
	`freq` int(11) NOT NULL,
	KEY `rel` (`rel`)
'
table_columns_relations_CORPNAME_head_rel='
	`head` varchar(100) NOT NULL,
	`rel` char(3) NOT NULL,
	`freq` int(11) NOT NULL,
	KEY `head` (`head`),
	KEY `rel` (`rel`)
'
table_columns_relations_CORPNAME_dep_rel='
	`dep` varchar(100) NOT NULL,
	`depextra` varchar(32) DEFAULT NULL,
	`rel` char(3) NOT NULL,
	`freq` int(11) NOT NULL,
	KEY `dep` (`dep`),
	KEY `rel` (`rel`)
'
table_columns_relations_CORPNAME_sentences='
        `id` int(11) NOT NULL,
	`sentence` varchar(64) NOT NULL,
	`start` int(11) NOT NULL,
	`end` int(11) NOT NULL,
	KEY `id` (`id`)
'

rels_table_prefix=relations_CORPNAME
rels_table_suffixes='@ _rel _head_rel _dep_rel _sentences'


warn () {
    echo "$progname: Warning: $1" >&2
}

error () {
    echo "$progname: $1" >&2
    exit 1
}

echo_verb () {
    if [ "x$verbose" != "x" ]; then
	echo "$@"
    fi
}

cleanup () {
    rm -f $tmpfname_base*
}

cleanup_abort () {
    cleanup
    exit 1
}


trap cleanup 0
trap cleanup_abort 1 2 13 15


usage () {
    cat <<EOF
Usage: $progname [options] filename ...

Import into Korp MySQL database data from files in TSV format. The
data files may be compressed with gzip, bzip2 or xz.

Each filename is assumed to be of the format CORPUS_TYPE.EXT, where
CORPUS is the name (id) of the corpus (in lower case), TYPE is the
type of the table and EXT is .tsv, possibly followed by the
compression extension. TYPE is one of the following: lemgrams,
timespans, rels, rels_rel, rels_head_rel, rels_dep_rel,
rels_sentences.

Options:
  -h, --help      show this help
  -t, --prepare-tables
                  create the necessary tables before importing the
                  data; for single-corpus tables, drop the table
                  first; for multi-corpus tables (lemgrams and
                  timespans), remove the rows for CORPUS
EOF
    exit 0
}


# Test if GNU getopt
getopt -T > /dev/null
if [ $? -eq 4 ]; then
    # This requires GNU getopt
    args=`getopt -o "ht" -l "help,prepare-tables" -n "$progname" -- "$@"`
    if [ $? -ne 0 ]; then
	exit 1
    fi
    eval set -- "$args"
fi
# If not GNU getopt, arguments of long options must be separated from
# the option string by a space; getopt allows an equals sign.

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	-t | --prepare-tables )
	    prepare_tables=1
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


if [ "x$MYSQL_USER" != "x" ]; then
    mysql_opt_user="--user $MYSQL_USER"
fi

get_cat () {
    case "$1" in
	*.gz )
	    echo zcat
	    ;;
	*.bz | *.bz2 )
	    echo bzcat
	    ;;
	*.xz )
	    echo xzcat
	    ;;
	* )
	    echo cat
	    ;;
    esac
}

make_tablename () {
    case "$1" in
	*_lemgrams.* )
	    echo lemgram_index
	    ;;
	*_timespans.* )
	    echo timespans
	    ;;
	*_rels.* | *_rels_*.* )
	    echo `basename "$1"` |
	    sed -e 's/\(.\+\)_rels\([^.]*\).*/relations_\U\1\E\2/'
	    ;;
    esac
}

make_corpname () {
    echo `basename "$1"` |
    sed -e 's/\(.\+\)_\(rels\(_.\+\)\?\|lemgrams\|timespans\).*/\1/'
}

get_colspec () {
    colspec_name=`echo "$1" | sed -e 's/_\([A-Z][A-Z0-9_]*[A-Z0-9]\)/_CORPNAME/'`
    echo `eval "echo \\$table_columns_$colspec_name"`
}

run_mysql () {
    mysql --local-infile $mysql_opt_user --batch --execute "$@" $dbname
}

create_table() {
    _tablename=$1
    _colspec=$2
    run_mysql "
CREATE TABLE IF NOT EXISTS $_tablename (
    $_colspec
    ) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8 DEFAULT COLLATE=utf8_bin;
"
}

delete_table_corpus_info() {
    _tablename=$1
    _corpname=$2
    run_mysql "DELETE FROM $tablename WHERE corpus='$_corpname';"
}

create_new_table() {
    _tablename=$1
    _colspec=$2
    run_mysql "DROP TABLE IF EXISTS $_tablename;"
    create_table $_tablename "$_colspec"
}

prepare_tables () {
    _tablename=$1
    _corpname=$2
    _colspec=$3
    case $_tablename in
	lemgram_index | timespans )
	    create_table $_tablename "$_colspec"
	    delete_table_corpus_info $_tablename $_corpname
	    ;;
	* )
	    create_new_table $tablename "$_colspec"
	    ;;
    esac
}

mysql_import () {
    file=$1
    tablename=`make_tablename "$file"`
    if [ "x$tablename" = x ]; then
	warn "Unrecognized file name: $file"
	return
    fi
    corpname=`make_corpname "$file"`
    cat=`get_cat "$file"`
    if [ "x$prepare_tables" != x ]; then
	colspec=`get_colspec $tablename`
	prepare_tables $tablename $corpname "$colspec"
    fi
    mkfifo $tablename.tsv
    ($cat $file > $tablename.tsv &)
    run_mysql "
	    set autocommit = 0;
	    set unique_checks = 0;
	    load data local infile '$tablename.tsv' into table $tablename fields escaped by '';
	    commit;
	    show count(*) warnings;
	    show warnings;"
    /bin/rm -f $tablename.tsv
}


for fname in "$@"; do
    echo "$fname"
    mysql_import "$fname"
done
