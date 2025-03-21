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
relations_format=new
table_name_template=@
show_warnings=1
mysql_extra_opts=
verbose=
show_progress=
progress_interval=300

# TODO: Maybe add options for these
max_connection_retries=5
reconnect_delay_base=30

mysql_datadir=/var/lib/mysql
mysql_datafile=$mysql_datadir/ibdata1
if [ ! -r $mysql_datadir ] || [ ! -e $mysql_datafile ]; then
    mysql_datadir=
    mysql_datafile=
fi

table_columns_lemgram_index='
	`lemgram` varchar(64) NOT NULL,
	`freq` int(11) DEFAULT NULL,
	`freq_prefix` int(11) DEFAULT NULL,
	`freq_suffix` int(11) DEFAULT NULL,
	`corpus` varchar(64) NOT NULL,
	PRIMARY KEY `lemgram_corpus` (`lemgram`, `corpus`, `freq`,
				      `freq_prefix`, `freq_suffix`)
'
table_columns_timespans='
	`corpus` varchar(64) NOT NULL,
	`datefrom` varchar(14) DEFAULT '"''"',
	`dateto` varchar(14) DEFAULT '"''"',
	`tokens` int(11) DEFAULT 0,
	KEY `corpus` (`corpus`)
'
table_columns_timedata='
	`corpus` varchar(64) NOT NULL DEFAULT '"''"',
	`datefrom` datetime NOT NULL DEFAULT '"'"'0000-00-00 00:00:00'"'"',
	`dateto` datetime NOT NULL DEFAULT '"'"'0000-00-00 00:00:00'"'"',
	`tokens` int(11) NOT NULL DEFAULT 0,
	PRIMARY KEY (`corpus`, `datefrom`, `dateto`)
'
table_columns_timedata_date='
	`corpus` varchar(64) NOT NULL DEFAULT '"''"',
	`datefrom` date NOT NULL DEFAULT '"'"'0000-00-00'"'"',
	`dateto` date NOT NULL DEFAULT '"'"'0000-00-00'"'"',
	`tokens` int(11) NOT NULL DEFAULT 0,
	PRIMARY KEY (`corpus`, `datefrom`, `dateto`)
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
# relations_new_rels_enum="ENUM('++','ADV','AN','AT','DT','ET','FV','head','IG','KA','NA','OBJ','PA','PL','SS','XX','YY')"
# TODO: Add an option for specifying the relation type type
rel_type="enum('SS','OBJ','ADV','AT','ET','PA','APP','AUX','CPL','CPR','CRD','MOD','OTH','OWN','VPT') NOT NULL DEFAULT 'SS'"
# # Alternatively:
# rel_type="char(4) NOT NULL"
table_columns_relations_new_CORPNAME='
	`id` int UNIQUE NOT NULL,
	`head` int NOT NULL,
	`rel` '"$rel_type"',
	`dep` int NOT NULL,
	`freq` int NOT NULL,
	`bfhead` bool NOT NULL,
	`bfdep` bool NOT NULL,
	`wfhead` bool NOT NULL,
	`wfdep` bool NOT NULL,
	PRIMARY KEY (`head`,`wfhead`,`dep`,`rel`,`freq`,`id`),
	KEY `dep-wfdep-head-rel-freq-id` (`dep`,`wfdep`,`head`,`rel`,`freq`,`id`),
	KEY `head-dep-bfhead-bfdep-rel-freq-id` (`head`,`dep`,`bfhead`,`bfdep`,`rel`,`freq`,`id`),
	KEY `dep-head-bfhead-bfdep-rel-freq-id` (`dep`,`head`,`bfhead`,`bfdep`,`rel`,`freq`,`id`)
'
table_columns_relations_new_CORPNAME_strings='
	`id` int UNIQUE NOT NULL,
	`string` varchar(100) NOT NULL,
	`stringextra` varchar(32) DEFAULT NULL,
	`pos` varchar(5) DEFAULT NULL,
	PRIMARY KEY (`string`,`id`,`pos`,`stringextra`),
	KEY `id-string-pos-stringextra` (`id`,`string`,`pos`,`stringextra`)
'
table_columns_relations_new_CORPNAME_rel='
	`rel` '"$rel_type"',
	`freq` int NOT NULL,
	PRIMARY KEY (`rel`,`freq`)
'
table_columns_relations_new_CORPNAME_head_rel='
	`head` int NOT NULL,
	`rel` '"$rel_type"',
	`freq` int NOT NULL,
	PRIMARY KEY (`head`,`rel`,`freq`)
'
table_columns_relations_new_CORPNAME_dep_rel='
	`dep` int NOT NULL,
	`rel` '"$rel_type"',
	`freq` int NOT NULL,
	PRIMARY KEY (`dep`,`rel`,`freq`)
'
table_columns_relations_new_CORPNAME_sentences='
	`id` int NOT NULL,
	`sentence` varchar(64) NOT NULL,
	`start` int NOT NULL,
	`end` int NOT NULL,
	KEY `id` (`id`)
'
table_columns_auth_license='
	`corpus` varchar(80) NOT NULL,
        `license` varchar(6) NOT NULL,
        PRIMARY KEY (`corpus`)
'
table_columns_auth_lbr_map='
	`lbr_id` varchar(255) DEFAULT NULL,
	`corpus` varchar(255) DEFAULT NULL
'

# The number of columns in the old and new formats for the head_rel
# table is the same, so we try to infer the format by the content of
# the first column, which is int in the new format and varchar in the
# old one.
relations_format_diff_int_column_num_CORPNAME_head_rel=1
relations_format_diff_int_column_format_CORPNAME_head_rel=new

relations_table_types="CORPNAME CORPNAME_strings CORPNAME_rel CORPNAME_head_rel CORPNAME_dep_rel CORPNAME_sentences"

# Filename base parts, only files for tables containing data for
# multiple corpora
filename_bases="lemgrams timedata timedata_date timespans auth_license auth_lbr_map"
filename_bases_commas="$(echo $filename_bases | sed 's/ /, /g')"
filename_bases_sed_re="$(echo $filename_bases | sed 's/ /\\|/g')"

# The table name corresponding to a multi-corpus filename base; if not
# defined, default to the filename base
tablename_lemgrams=lemgram_index

# Multicorpus tables to with other tables refer via foreign key
# constraints, so that rows in them cannot be deleted. In practice,
# this does not help, since trying to update the data without deleting
# it results in a violation of the primary key constraint.
# tables_no_delete_rows="auth_license"

shortopts="htI:v"
longopts="help,prepare-tables,imported-file-list:,relations-format:,table-name-template:,hide-warnings,mysql-program:,mysql-binary:mysql-options:,verbose,show-progress,progress-interval:"

. $progdir/korp-lib.sh

tmpfname_base=$tmp_prefix.tmp

import_errorfile=$tmpfname_base.import_error
progress_errorfile=$tmpfname_base.progress_error

# File containing the period of time under which new database imports
# are not started (as start and end time as hh:mm[:ss] on the same
# line, separated by whitespace; comment lines beginning with a # are
# ignored)
pause_period_fname=$corpus_root/mysql-import-pause.txt


usage () {
    cat <<EOF
Usage: $progname [options] filename ...

Import into Korp MySQL database data from files in TSV format. The data files
may be compressed with gzip, bzip2 or xz.

Each filename is assumed to be of the format CORPUS_TYPE.EXT, where CORPUS is
the name (id) of the corpus (in lower case), TYPE is the type of the table and
EXT is .tsv, possibly followed by the compression extension. TYPE is one of
the following: lemgrams, timedata, timedata_date, timespans, rels, rels_rel,
rels_head_rel, rels_dep_rel, rels_sentences, rels_strings.

Options:
  -h, --help      show this help
  -t, --prepare-tables
                  create the necessary tables before importing the data; for
                  single-corpus tables, drop the table first; for multi-corpus
                  tables (lemgrams, timedata, timedata_date and timespans),
                  remove the rows for CORPUS
  -I, --imported-file-list FILE
                  do not import files listed in FILE, and write the names of
                  imported files to FILE
  --relations-format new|old|auto
                  the format for word picture relation tables: "new" for Korp
                  backend 2.5 and later, "old" for Korp backend versions 2 to
                  2.3, or "auto" for inferring automatically (default:
                  "$relations_format")
  --table-name-template TEMPLATE
                  use TEMPLATE for naming tables; TEMPLATE should contain @
                  for the default table (base) name (lemgram_index, timedata,
                  timedata_date, timespans, relations) (default: $table_name_template)
  --hide-warnings
                  do not show possible MySQL warnings
  --mysql-program PROG
                  run PROG as the MySQL client program (mysql); the program
                  name in PROG may also be followed by a space and mysql
                  options to be specified before other options, in particular
                  --defaults-file; useful with multiple instances of MySQL
  --mysql-options OPTS
                  pass OPTS as additional options to the MySQL client
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
	--mysql-program | --mysql-binary )
	    shift
	    mysql_bin=$1
	    ;;
	--mysql-options )
	    shift
	    mysql_extra_opts=$1
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


mysql_opts="$mysql_opts --local-infile --skip-reconnect $mysql_extra_opts"

if [ "x$mysql_bin" = x ]; then
    error "$mysql_error"
fi


# If $pause_period_fname exists and if the current time is within the
# period specified in the file, sleep until the end of the period
check_pause_import () {
    local start end tmpfile
    if [ ! -r "$pause_period_fname" ]; then
        return
    fi
    tmpfile=$tmp_prefix.pause_period
    # No pipe, so that start and end are set in this process
    {
        # The start and end time can be on the same line or on
        # different lines; allow empty and comment lines beginning
        # with a #
        grep -v '^ *#' "$pause_period_fname" |
            grep -v '^[[:space:]]*$' |
            tr '\n' ' '
        printf '\n'
    } > $tmpfile
    read start end < $tmpfile
    if ! time_is_valid start "$start" || ! time_is_valid end "$end"; then
        return
    fi
    if time_is_between $start $end; then
        echo "Pausing importing until $(strip_seconds $end) as specified in $pause_period_fname"
        sleep_until $end
    fi
}

# Return success if the argument is a valid time (hh:mm[:ss]);
# otherwise, output a warning and return failure
time_is_valid () {
    local type time
    type=$1
    time=$2
    if echo "$time" |
            grep -Esq '^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$';
    then
        return 0
    else
        warn "Invalid pause $type time in $pause_period_fname: \"$time\""
        return 1
    fi
}

# Return success if the current time is between the times given as
# arguments (as hh:mm[:ss])
time_is_between () {
    local current start end
    start=$(convert_to_minutes $1)
    end=$(convert_to_minutes $2)
    current=$(get_current_time)
    if [ $start -lt $end ]; then
        # 02:00 04:00
        if [ $current -ge $start ] && [ $current -lt $end ]; then
            return 0
        fi
    elif [ $current -ge $start ] || [ $current -lt $end ]; then
        # 23:00 01:00
        return 0
    fi
    return 1
}

# Output the current time in minutes since midnight
get_current_time () {
    echo $(convert_to_minutes $(date '+%H:%M'))
}

# Convert hh:mm[:ss] to minutes (hh * 60 + mm)
convert_to_minutes () {
    local time
    time=$(strip_seconds $1)
    echo $(( $(strip_zero ${time%:*}) * 60 + $(strip_zero ${time#*:}) ))
}

# Strip seconds from argument: convert hh:mm[:ss] to hh:mm
strip_seconds () {
    local time
    time=$1
    if [ "${time%:*}" != "${time%%:*}" ]; then
        time=${time%:*}
    fi
    echo "$time"
}

# Strip leading zero from the argument
strip_zero () {
    local time
    time=$1
    echo "${time#0}"
}

# Sleep until the time given as an argument (hh:mm[:ss]), at minute
# precision
sleep_until () {
    local endtime current mins
    endtime=$(convert_to_minutes $1)
    current=$(get_current_time)
    if [ $current -le $endtime ]; then
        mins=$(( $endtime - $current ))
    else
        # If $endtime < $current, count the minutes from $current to
        # midnight and add $endtime
        mins=$(( 24 * 60 - $current + $endtime ))
    fi
    sleep $(( $mins * 60 ))
}

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

get_tablename_for_filename_base () {
    local fname_base tablename_base
    fname_base=$1
    tablename_base=$(eval echo "\$tablename_$fname_base")
    if [ "x$tablename_base" = "x" ]; then
	tablename_base=$fname_base
    fi
    echo $tablename_base
}

# Get the table name base based on the filename argument.
get_file_tablename_base () {
    local _fname fname_base
    _fname=$1
    for fname_base in $filename_bases; do
	case "$_fname" in
	    *_$fname_base.* )
		echo $(get_tablename_for_filename_base $fname_base)
		break
		;;
	esac
    done
}

make_tablename () {
    case "$1" in
	*_rels.* | *_rels_*.* )
	    table_basename=$(fill_tablename_template relations)
	    echo `basename "$1"` |
	    sed -e 's/\(.\+\)_rels\([^.]*\).*/'"$table_basename"'_\U\1\E\2/'
	    ;;
	* )
	    tablename_base=$(get_file_tablename_base "$1")
	    if [ "x$tablename_base" != x ]; then
		fill_tablename_template $tablename_base
	    fi
	    ;;
    esac
}

make_corpname () {
    echo `basename "$1"` |
    sed -e 's/\(.\+\)_\(rels\(_.\+\)\?\|'"$filename_bases_sed_re"'\).*/\U\1\E/'
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
	    if [ "x$int_format" = xnew ]; then
		echo relations_new
	    else
		echo relations
	    fi
	fi
	return
    fi
    warn "Could not infer relations format for file $_file; assuming 'new'"
    echo relations_new
}

get_colspec_name () {
    case "$1" in
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
	* )
	    colspec_name=$(get_file_tablename_base "$1")
	    ;;
    esac
    echo $colspec_name
}

get_colspec () {
    echo `eval "echo \\$table_columns_$1"`
}

run_mysql_report_errors () {
    local tablename _errorfile
    tablename=$1
    # Return the error information via a file, since setting the value
    # of a variable does not seem to propagate to the caller.
    _errorfile=$2
    shift 2
    # $$ is the pid of the parent shell (script) even in subshells, so
    # use a md5sum of the arguments to make the name of the teefile
    # unique
    teefile=$_errorfile.tee
    run_mysql --table $tablename "$@" 2>&1 |
    tee $teefile
    grep '^ERROR ' $teefile |
    head -1 |
    sed -e 's/^ERROR \([0-9]\+\).*/\1/' > $_errorfile
    rm $teefile
}

create_table() {
    _tablename=$1
    _colspec=$2
    run_mysql --table $_tablename "
CREATE TABLE IF NOT EXISTS \`$_tablename\` (
    $_colspec
    ) ENGINE=InnoDB
      ROW_FORMAT=COMPRESSED;
"
}

delete_table_corpus_info() {
    _tablename=$1
    _corpname=$2
    run_mysql --table $_tablename \
	"DELETE FROM \`$_tablename\` WHERE corpus='$_corpname';"
}

create_new_table() {
    _tablename=$1
    _colspec=$2
    run_mysql --table $_tablename "DROP TABLE IF EXISTS \`$_tablename\`;"
    create_table $_tablename "$_colspec"
}

get_multicorpus_tablenames () {
    local tablename
    for fname_base in $filename_bases; do
	echo $(get_tablename_for_filename_base $fname_base)
    done
}

prepare_tables () {
    _tablename=$1
    _corpname=$2
    _colspec=$3
    for tblname in $(get_multicorpus_tablenames); do
	if [ $tblname = $_tablename ]; then
	    create_table $_tablename "$_colspec"
	    # if ! word_in $_tablename "$tables_no_delete_rows"; then
	    delete_table_corpus_info $_tablename $_corpname
	    # fi
	    return
	fi
    done
    # Otherwise $_tablename not in $multicorpus_tablenames
    create_new_table $tablename "$_colspec"
}

get_mysql_datafile_size () {
    if [ "x$mysql_datafile" != "x" ]; then
	get_filesize "$mysql_datafile"
    fi
}

show_mysql_datafile_size () {
    datasize=$1
    datasize_prev=$2
    if [ "x$datasize" != "x" ] && [ "x$mysql_datafile" != "x" ]; then
	echo \
	    "  MySQL data file size: $datasize = "`calc_gib $datasize`" GiB"
	if [ "x$datasize_prev" != "x" ]; then
	    datasize_diff=`expr $datasize - $datasize_prev`
	    echo "  MySQL data file size increase: $datasize_diff = "`calc_gib $datasize_diff`" GiB"
	fi
    fi
}

get_mysql_table_rowcount () {
    # The row count is only an approximation for InnoDB tables.
    run_mysql_report_errors $1 $progress_errorfile "SELECT table_rows FROM information_schema.tables WHERE table_name='$1' \G ; " |
    grep rows |
    cut -d':' -f2 |
    tr -d ' '
}

report_progress () {
    # This function should be run on the background, since it contains
    # a non-terminating loop. Adapted from
    # http://derwiki.tumblr.com/post/24490758395/loading-half-a-billion-rows-into-mysql
    tablename=$1
    total_rows=$2
    init_rows=$(get_mysql_table_rowcount $tablename)
    prev_rows=0
    sleep $progress_interval
    while :; do
	while :; do
	    imported_rows=$(($(get_mysql_table_rowcount $tablename) - $init_rows))
	    new_imported_rows=$(($imported_rows - $prev_rows))
	    # If the number of imported rows is negative or the number
	    # of rows imported since the previous round is negative or
	    # zero (due to the fluctuating approximate row count), try
	    # again.
	    if [ $imported_rows -lt 0 ] || [ $new_imported_rows -le 0 ]; then
		continue
	    fi
	    if [ ! -s $progress_errorfile ] && [ "x$imported_rows" != x ]; then
		row_percentage=$(
		    awk 'BEGIN {printf "%.2f", '"$imported_rows"' / '"$total_rows"' * 100}'
		)
		secs=$(date +%s)
		secs_remaining=$(
		    awk 'BEGIN {printf "%d", ('"$total_rows"' - '"$imported_rows"') / (('"$imported_rows"' - '"$prev_rows"') / '"$progress_interval"')}'
		)
		# echo $init_rows $prev_rows $imported_rows $row_percentage $secs $secs_remaining
		# The imprecision of fast InnoDB row counts may result
		# in negative progress. Instead of showing such
		# information, try again after waiting a second.
		if awk "BEGIN {exit ($secs_remaining < 0 || $imported_rows < $prev_rows || $row_percentage < 0 || $row_percentage > 100)}"; then
		    echo "  "$(date +"%F %T")" rows: $imported_rows ($row_percentage%); est. time remaining: $secs_remaining s"
		    prev_rows=$imported_rows
		    break
		else
		    sleep 1
		fi
	    fi
	done
	sleep $progress_interval
    done
}

has_column_name_header () {
    file=$1
    colspec=$2
    # The header row is detected if the first word on the first row of
    # the file is the same as the name of the first column in the
    # column specification.
    file_firstval=$(comprcat $file | head -1 | cut -d"$tab" -f1)
    first_colname=$(echo $colspec | awk '{print $1}' | tr -d '`')
    [ "x$file_firstval" = "x$first_colname" ]
    return $?
}

mysql_import_main () {
    file=$1
    corpname=$2
    tablename=$3
    colspec=$4
    if [ "x$prepare_tables" != x ]; then
	prepare_tables $tablename $corpname "$colspec"
    fi
    fifo=$tmpfname_base.$tablename.fifo
    pipe_skip_header=
    if has_column_name_header "$file" "$colspec"; then
	pipe_skip_header="| tail -n+2"
    fi
    mkfifo $fifo
    (
	eval "comprcat $file $pipe_skip_header" > $fifo &
    )
    # Import optimization ideas (for InnoDB tables) taken from
    # http://derwiki.tumblr.com/post/24490758395/loading-half-a-billion-rows-into-mysql
    # Disabling foregin key checks probably does not matter, as
    # foreign keys are not currently used. sql_log_bin cannot be
    # disabled by a non-super user.
    mysql_cmds="
	    set unique_checks = 0;
            set foreign_key_checks = 0;
            set session tx_isolation = 'READ-UNCOMMITTED';
	    load data local infile '$fifo' into table \`$tablename\` fields escaped by '';"
    if [ "x$show_warnings" != x ]; then
	echo '  MySQL output:'
	mysql_cmds="$mysql_cmds
	    show count(*) warnings;
	    show warnings;"
    fi
    if [ "x$show_progress" != x ]; then
	total_rows=$(eval "comprcat $file $pipe_skip_header | wc -l")
	report_progress $tablename $total_rows &
	progress_pid=$!
    fi
    run_mysql_report_errors $tablename $import_errorfile "$mysql_cmds" |
    awk '{print "    " $0}'
    if [ "x$show_progress" != x ]; then
	kill $progress_pid
	echo "  "$(date +"%F %T")" rows: $total_rows (100.00%)"
    fi
    /bin/rm -f $fifo
}

mysql_import_retry_loop () {
    file=$1
    connection_retries=0
    reconnect_delay=$reconnect_delay_base
    # set -vx
    while true; do
	mysql_import_main "$@"
	mysql_error=$(cat $import_errorfile)
	case "$mysql_error" in
	    "" )
		break
		;;
	    2013 | 2002 )
		# Lost connection or can't connect to server
		if [ $connection_retries -lt $max_connection_retries ]; then
		    connection_retries=$(($connection_retries + 1))
		    echo "Waiting $reconnect_delay s before trying to reconnect to the MySQL server"
		    sleep $reconnect_delay
		    reconnect_delay=$(($reconnect_delay * 2))
		    verbose echo "Trying to reconnect (attempt $connection_retries/$max_connection_retries)"
		else
		    error "Giving up importing $1 after $max_connection_retries attempts; aborting"
		fi
		;;
	    * )
		error "Aborting because of MySQL errors"
		;;
	esac
    done
    # set +vx
}

mysql_import () {
    file=$1
    if [ ! -e "$file" ]; then
	warn "No such file: $file"
	return
    elif [ ! -r "$file" ]; then
	warn "Cannot read file $file"
	return
    fi
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
    colspec_name=$(get_colspec_name $file)
    colspec=$(get_colspec $colspec_name)
    if [ x"$colspec" = x ] && [ "x$prepare_tables" != x ]; then
	warn "Could not find columns specification for file $file; skipping"
	return
    fi
    check_pause_import
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
    mysql_import_retry_loop $file $corpname $tablename "$colspec"
    if [ "x$verbose" != x ]; then
	date +'  End: %F %T'
	secs_1=`date +%s`
	echo "  Elapsed: "`expr $secs_1 - $secs_0`" s"
	datasize_1=`get_mysql_datafile_size`
	show_mysql_datafile_size $datasize_1 $datasize_0
    fi
    if [ "x$imported_file_list" != x ]; then
	echo "$file_base" >> "$imported_file_list"
    fi
}


init_table_column_counts
for fname in "$@"; do
    mysql_import "$fname"
done
