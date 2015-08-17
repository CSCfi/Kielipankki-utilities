#! /bin/sh
# -*- coding: utf-8 -*-

# Usage: korp-mysql-import.sh [options] filename ...
#
# For more information, run korp-mysql-import.sh --help

# TODO:
# - Support importing to table corpus_info


progname=`basename $0`
progdir=`dirname $0`

dbname=korp

prepare_tables=
imported_file_list=
relations_format=auto
table_name_template=@
show_warnings=1
verbose=
show_progress=
progress_interval=300

mysql_datadir=/var/lib/mysql
mysql_datafile=$mysql_datadir/ibdata1
if [ ! -r $mysql_datadir ]; then
    mysql_datadir=
    mysql_datafile=
fi

table_columns_lemgram_index='
	`lemgram` varchar(64) NOT NULL,
	`freq` int(11) DEFAULT NULL,
	`freq_prefix` int(11) DEFAULT NULL,
	`freq_suffix` int(11) DEFAULT NULL,
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
relations_new_rels_enum="ENUM('++','ADV','AN','AT','DT','ET','FV','head','IG','KA','NA','OBJ','PA','PL','SS','XX','YY')"
# Below alternatively:	`rel` '$relations_new_rels_enum' NOT NULL,
table_columns_relations_new_CORPNAME='
        `id` int UNIQUE NOT NULL,
	`head` int NOT NULL,
	`rel` char(4) NOT NULL,
	`dep` int NOT NULL,
	`freq` int NOT NULL,
	`bfhead` bool NOT NULL,
	`bfdep` bool NOT NULL,
	`wfhead` bool NOT NULL,
	`wfdep` bool NOT NULL,
	PRIMARY KEY (`id`),
	KEY `head` (`head`),
	KEY `dep` (`dep`),
        KEY `bfhead` (`bfhead`),
        KEY `bfdep` (`bfdep`),
        KEY `wfhead` (`wfhead`),
        KEY `wfdep` (`wfdep`)
'
table_columns_relations_new_CORPNAME_strings='
	`id` int UNIQUE NOT NULL,
	`string` varchar(100) NOT NULL,
	`stringextra` varchar(32) DEFAULT NULL,
	`pos` varchar(5) DEFAULT NULL,
	PRIMARY KEY (`id`),
	KEY `string` (`string`)
'
table_columns_relations_new_CORPNAME_rel=$table_columns_relations_CORPNAME_rel
table_columns_relations_new_CORPNAME_head_rel='
	`head` int NOT NULL,
	`rel` char(4) NOT NULL,
	`freq` int NOT NULL,
	KEY `head` (`head`),
	KEY `rel` (`rel`)
'
table_columns_relations_new_CORPNAME_dep_rel='
	`dep` int NOT NULL,
	`rel` char(4) NOT NULL,
	`freq` int NOT NULL,
	KEY `dep` (`dep`),
	KEY `rel` (`rel`)
'
table_columns_relations_new_CORPNAME_sentences=$table_columns_relations_CORPNAME_sentences

# The number of columns in the old and new formats for the head_rel
# table is the same, so we try to infer the format by the content of
# the first column, which is int in the new format and varchar in the
# old one.
relations_format_diff_int_column_num_CORPNAME_head_rel=1
relations_format_diff_int_column_format_CORPNAME_head_rel=new

relations_table_types="CORPNAME CORPNAME_strings CORPNAME_rel CORPNAME_head_rel CORPNAME_dep_rel CORPNAME_sentences"

shortopts="htI:v"
longopts="help,prepare-tables,imported-file-list:,relations-format:,table-name-template:,hide-warnings,verbose,show-progress,progress-interval:"

. $progdir/korp-lib.sh

tmpfname_base=$tmp_prefix.tmp


usage () {
    cat <<EOF
Usage: $progname [options] filename ...

Import into Korp MySQL database data from files in TSV format. The data files
may be compressed with gzip, bzip2 or xz.

Each filename is assumed to be of the format CORPUS_TYPE.EXT, where CORPUS is
the name (id) of the corpus (in lower case), TYPE is the type of the table and
EXT is .tsv, possibly followed by the compression extension. TYPE is one of
the following: lemgrams, timespans, rels, rels_rel, rels_head_rel,
rels_dep_rel, rels_sentences, rels_strings.

Options:
  -h, --help      show this help
  -t, --prepare-tables
                  create the necessary tables before importing the data; for
                  single-corpus tables, drop the table first; for multi-corpus
                  tables (lemgrams and timespans), remove the rows for CORPUS
  -I, --imported-file-list FILE
                  do not import files listed in FILE, and write the names of
                  imported files to FILE
  --relations-format auto|new|old
                  the format for word picture relation tables: "auto" for
                  inferring automatically, "new" for Korp backend 2.5 and
                  later, or "old" for Korp backend versions 2 to 2.3 (default:
                  "$relations_format")
  --table-name-template TEMPLATE
                  use TEMPLATE for naming tables; TEMPLATE should contain @
                  for the default table (base) name (lemgram_index, timespans,
                  relations) (default: $table_name_template)
  --hide-warnings
                  do not show possible MySQL warnings
  -v, --verbose   show input file sizes, import times and MySQL data file size
                  increase
  --show-progress
                  show import progress as the percentage of rows imported
  --progress-interval SECS
                  show import progress information every SECS seconds
                  (default: $progress_interval)
EOF
    exit 0
}

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	-t | --prepare-tables )
	    prepare_tables=1
	    ;;
	-I | --imported-file-list )
	    shift
	    imported_file_list=$1
	    if [ ! -e "$imported_file_list" ]; then
		touch "$imported_file_list"
	    fi
	    ;;
	--relations-format )
	    shift
	    case "$1" in
		auto | new | old )
		    relations_format=$1
		    ;;
		* )
		    warn 'Valid arguments for --relations-format are "auto", "new" and "old"'
		    ;;
	    esac
	    ;;
	--table-name-template )
	    shift
	    table_name_template=$1
	    ;;
	--hide-warnings )
	    show_warnings=
	    ;;
	-v | --verbose )
	    verbose=1
	    ;;
	--show-progress )
	    show_progress=1
	    ;;
	--progress-interval )
	    shift
	    progress_interval=$1
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

init_table_column_counts () {
    for tabletype in $relations_table_types; do
	for suffix in "" new_; do
	    colcnt=$(
		eval echo '"'"\$table_columns_relations_$suffix$tabletype"'"' |
		grep -c '^[ 	]*`'
	    )
	    eval "col_count_relations_$suffix$tabletype=$colcnt"
	done
    done
}

fill_tablename_template () {
    echo "$table_name_template" |
    sed -e "s/@/$1/"
}

make_tablename () {
    case "$1" in
	*_lemgrams.* )
	    fill_tablename_template lemgram_index
	    ;;
	*_timespans.* )
	    fill_tablename_template timespans
	    ;;
	*_rels.* | *_rels_*.* )
	    table_basename=$(fill_tablename_template relations)
	    echo `basename "$1"` |
	    sed -e 's/\(.\+\)_rels\([^.]*\).*/'"$table_basename"'_\U\1\E\2/'
	    ;;
    esac
}

make_corpname () {
    echo `basename "$1"` |
    sed -e 's/\(.\+\)_\(rels\(_.\+\)\?\|lemgrams\|timespans\).*/\1/'
}

infer_relations_format () {
    _file=$1
    reltable=$(echo "$1" | sed -e 's/\(.\+\)_rels\([^.]*\).*/CORPNAME\2/')
    columns_old=$(eval "echo \$table_columns_relations_$reltable")
    columns_new=$(eval "echo \$table_columns_relations_new_$reltable")
    # If the table type is "strings" or the old and new table
    # definitions are equal, use the new format.
    if [ "x$columns_new" != x ] && [ "x$reltable" = xstrings ] ||
	[ x"$columns_new" = x"$columns_old" ]
    then
	echo relations_new
	return
    fi
    # If the number of columns in the formats differs, use the format
    # with the same number of columns as in the input file.
    col_count_old=$(eval "echo \$col_count_relations_$reltable")
    col_count_new=$(eval "echo \$col_count_relations_new_$reltable")
    if [ $col_count_old != $col_count_new ]; then
	col_count_file=$(
	    comprcat $_file |
	    head -1 |
	    tr '\t' '\n' |
	    wc -l
	)
	if [ $col_count_file = $col_count_old ]; then
	    echo relations
	elif [ $col_count_file = $col_count_new ]; then
	    echo relations_new
	fi
	return
    fi
    # If a column type differs (int vs. varchar), check that for the
    # first 20 rows in the input file.
    int_column_num=$(
	eval "echo \$relations_format_diff_int_column_num_$reltable")
    if [ "x$int_column_num" != x ]; then
	non_int_cnt=$(
	    comprcat $_file |
	    head -20 |
	    cut -d'	' -f$int_column_num |
	    grep -E -cv '^[0-9]+$'
	)
	int_format=$(
	    eval "echo \$relations_format_diff_int_column_format_$reltable")
	if [ $non_int_cnt != 0 ]; then
	    if [ "x$int_format" = xnew ]; then
		echo relations
	    else
		echo relations_new
	    fi
	else
	    if [ "x$int_format" = new ]; then
		echo relations_new
	    else
		echo relations
	    fi
	fi
	return
    fi
    warn "Could not infer relations format for file $_file; please specify --relations-format=new|old"
}

get_colspec_name () {
    case "$1" in
	*_lemgrams.* )
	    colspec_name=lemgram_index
	    ;;
	*_timespans.* )
	    colspec_name=timespans
	    ;;
	*_rels.* | *_rels_*.* )
	    if [ "$relations_format" = "old" ]; then
		base=relations
	    elif [ "$relations_format" = "new" ]; then
		base=relations_new
	    else
		base=$(infer_relations_format "$1")
	    fi
	    colspec_name=$(
		echo "$1" |
		sed -e 's/.\+_rels\([^.]*\).*/'$base'_CORPNAME\1/'
	    )
	    ;;
    esac
    echo $colspec_name
}

get_colspec () {
    echo `eval "echo \\$table_columns_$1"`
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

get_mysql_datafile_size () {
    if [ "x$mysql_datafile" != "x" ]; then
	get_filesize "$mysql_datafile"
    fi
}

show_mysql_datafile_size () {
    datasize=$1
    datasize_prev=$2
    if [ "x$datasize" != "x" ]; then
	echo \
	    "  MySQL data file size: $datasize = "`calc_gib $datasize`" GiB"
	if [ "x$datasize_prev" != "x" ]; then
	    datasize_diff=`expr $datasize - $datasize_prev`
	    echo "  MySQL data file size increase: $datasize_diff = "`calc_gib $datasize_diff`" GiB"
	fi
    fi
}

report_progress () {
    # This function should be run on the background, since it contains
    # a non-terminating loop. Adapted from
    # http://derwiki.tumblr.com/post/24490758395/loading-half-a-billion-rows-into-mysql
    total_rows=$1
    sleep $progress_interval
    prev_rows=0
    while :; do
	imported_rows=$(
	    run_mysql "SELECT table_rows FROM information_schema.tables WHERE table_name='$tablename' \G ; " |
	    grep rows |
	    cut -d':' -f2 |
	    tr -d ' '
	)
	row_percentage=$(
	    awk 'BEGIN {printf "%.2f", '$imported_rows' / '$total_rows' * 100}'
	)
	secs=$(date +%s)
	secs_remaining=$(
	    awk 'BEGIN {printf "%d", ('$total_rows' - '$imported_rows') / (('$imported_rows' - '$prev_rows') / '$progress_interval')}'
	)
	echo "  "$(date +"%F %T")" rows: $imported_rows ($row_percentage%); est. time remaining: $secs_remaining s"
	prev_rows=$imported_rows
	sleep $progress_interval
    done
}

mysql_import () {
    file=$1
    file_base=`basename $file`
    if [ "x$imported_file_list" != x ] &&
	grep -Fq "$file_base" "$imported_file_list"; then
	echo "$file already imported"
	return
    fi
    tablename=`make_tablename "$file"`
    if [ "x$tablename" = x ]; then
	warn "Unrecognized file name: $file"
	return
    fi
    corpname=`make_corpname "$file"`
    if [ "x$prepare_tables" != x ]; then
	colspec_name=$(get_colspec_name $file)
	colspec=$(get_colspec $colspec_name)
	if [ x"$colspec" = x ]; then
	    warn "Could not find columns specification for file $file; skipping"
	    return
	fi
	prepare_tables $tablename $corpname "$colspec"
    fi
    fifo=$tmpfname_base.$tablename.fifo
    mkfifo $fifo
    (comprcat $file > $fifo &)
    echo Importing $fname into table $tablename
    if [ "x$verbose" != x ]; then
	case $colspec_name in
	    relations_new* )
		echo "  Using relations format 'new'"
		;;
	    relations* )
		echo "  Using relations format 'old'"
		;;
	esac
	filesize=`get_filesize "$1"`
	echo '  File size: '$filesize' = '`calc_gib $filesize`' GiB'
	secs_0=`date +%s`
	datasize_0=`get_mysql_datafile_size`
	show_mysql_datafile_size $datasize_0
	date +'  Start: %F %T'
    fi
    # Import optimization ideas (for InnoDB tables) taken from
    # http://derwiki.tumblr.com/post/24490758395/loading-half-a-billion-rows-into-mysql
    # Disabling foregin key checks probably does not matter, as
    # foreign keys are not currently used. sql_log_bin cannot be
    # disabled by a non-super user.
    mysql_cmds="
	    set unique_checks = 0;
            set foreign_key_checks = 0;
            set session tx_isolation = 'READ-UNCOMMITTED';
	    load data local infile '$fifo' into table $tablename character set utf8 fields escaped by '';"
    if [ "x$show_warnings" != x ]; then
	echo '  MySQL output:'
	mysql_cmds="$mysql_cmds
	    show count(*) warnings;
	    show warnings;"
    fi
    if [ "x$show_progress" != x ]; then
	total_rows=$(comprcat $file | wc -l)
	report_progress $total_rows &
	progress_pid=$!
    fi
    run_mysql "$mysql_cmds" |
    awk '{print "    " $0}'
    if [ "x$show_progress" != x ]; then
	kill $progress_pid
	echo "  "$(date +"%F %T")" rows: $total_rows (100.00%)"
    fi
    if [ "x$verbose" != x ]; then
	date +'  End: %F %T'
	secs_1=`date +%s`
	echo "  Elapsed: "`expr $secs_1 - $secs_0`" s"
	datasize_1=`get_mysql_datafile_size`
	show_mysql_datafile_size $datasize_1 $datasize_0
    fi
    /bin/rm -f $fifo
    if [ "x$imported_file_list" != x ]; then
	echo "$file_base" >> "$imported_file_list"
    fi
}


init_table_column_counts
for fname in "$@"; do
    mysql_import "$fname"
done
