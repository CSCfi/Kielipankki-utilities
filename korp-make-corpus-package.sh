#! /bin/bash
# -*- coding: utf-8 -*-

# Make a Korp corpus installation and archive package from CWB corpus
# files and Korp MySQL database information

# TODO:
# - Options for including a readme file and corpus conversion scripts
#   (and possibly also documentation and Korp configuration, or a more
#   generic way of specifying a (target) directory and its contents).
# - Check that the CWB data files include all the necessary indices
#   produced by cwb-make. Possibly also other sanity checks for the
#   corpus.
# - Working --verbose (or --quiet).
# - Update MySQL dumps if older than the database files (or if an
#   option is specified).


progname=`basename $0`

corpus_root=${CORPUS_ROOT:-/v/corpora}
# These will be set later based on $corpus_root, which may be modified
# by options
target_corpus_root=$TARGET_CORPUS_ROOT
regdir=$CORPUS_REGISTRY
datadir=$CORPUS_DATADIR
sqldir=$CORPUS_SQLDIR
pkgdir=$CORPUS_PKGDIR
tsvdir=$CORPUS_TSVDIR
tmpdir=${TMPDIR:-${TEMPDIR:-${TMP:-${TEMP:-/tmp}}}}

regsubdir=registry
datasubdir=data
sqlsubdir=sql
pkgsubdir=ida

compress=gzip
verbose=
dbformat=auto

archive_ext_none=tar
archive_ext_gzip=tgz
archive_ext_bzip=tbz
archive_ext_xz=txz

sql_file_types="lemgrams rels timespans"
sql_file_types_multicorpus="lemgrams timespans"
sql_table_name_lemgrams=lemgram_index
rels_tables_basenames="@ rel head_rel dep_rel sentences"

for grp in korp clarin; do
    if groups | grep -qw $grp; then
	filegroup=$grp
	break
    fi
done
if [ "x$filegroup" = x ]; then
    filegroup=`groups | cut -d' ' -f1`
fi

# Korp MySQL database
korpdb=korp
# Unless specified via environment variables, assume that the Korp
# MySQL database user and password are specified in a MySQL option
# file
mysql_opts=
if [ "x$KORP_MYSQL_USER" != "x" ]; then
    mysql_opts=--user=$KORP_MYSQL_USER
else
    mysql_opts=--user=korp
fi
if [ "x$KORP_MYSQL_PASSWORD" != "x" ]; then
    mysql_opts="$mysql_opts --password=$KORP_MYSQL_PASSWORD"
fi


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
    if [ "x$tmp_prefix" != "x" ]; then
	rm -rf $tmp_prefix.*
    fi
}

cleanup_abort () {
    cleanup
    exit 1
}


trap cleanup 0
trap cleanup_abort 1 2 13 15


usage () {
    cat <<EOF
Usage: $progname [options] corpus_name [corpus_id ...]

Make an archive package for corpus corpus_name, containing the Korp
corpora corpus_id ... (or corpus_name if corpus_id not specified).

Options:
  -h, --help      show this help
  -c, --corpus-root DIR
                  use DIR as the root directory of corpus files for the
                  source files (default: $corpus_root)
  --target-corpus-root DIR
                  use DIR as the root directory of corpus files for the
                  target files (to adjust paths in the corpus registry files)
                  (default: $target_corpus_root)
  -p, --package-dir DIR
                  put the resulting package to a subdirectory CORPUS_NAME
                  under the directory DIR (default: CORPUS_ROOT/$pkgsubdir)
  -r, --registry DIR
                  use DIR as the CWB registry (default: CORPUS_ROOT/$regsubdir)
  -s, --sql-dir DIRTEMPL
                  use DIRTEMPL as the directory template for Korp MySQL
                  dumps; DIRTEMPL is a directory name possibly containing
                  placeholder {corpname} for corpus name or {corpid} for
                  corpus id (default: CORPUS_ROOT/$sqlsubdir)
  -t, --tsv-dir DIRTEMPL
                  use DIRTEMPL as the directory template for for Korp MySQL
                  TSV data files (default: CORPUS_ROOT/$sqlsubdir)
  -f, --database-format FMT
                  include database files in format FMT: either sql (SQL),
                  tsv (TSV) or auto (SQL or TSV, whichever files are newer)
                  (default: $dbformat)
  -z, --compress PROG
                  compress files with PROG; "none" for no compression
                  (default: $compress)
EOF
    exit 0
}


# Test if GNU getopt
getopt -T > /dev/null
if [ $? -eq 4 ]; then
    # This requires GNU getopt
    args=`getopt -o "hc:p:r:s:t:f:vz:" -l "help,corpus-root:,target-corpus-root:,package-dir:,registry:,sql-dir:,tsv-dir:,database-format:,compress:,verbose" -- "$@"`
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
	-c | --corpus-root )
	    corpus_root=$2
	    shift
	    ;;
	--target-corpus-root )
	    target_corpus_root=$2
	    shift
	    ;;
	-p | --package-dir )
	    pkgdir=$2
	    shift
	    ;;
	-r | --registry )
	    regdir=$2
	    shift
	    ;;
	-s | --sql-dir )
	    sqldir=$2
	    shift
	    ;;
	-t | --tsv-dir )
	    tsvdir=$2
	    shift
	    ;;
	-f | --database-format )
	    case "$2" in
		sql | SQL )
		    dbformat=sql
		    ;;
		tsv | TSV )
		    dbformat=tsv
		    ;;
		auto | automatic )
		    dbformat=auto
		    ;;
		* )
		    warn "Invalid database format '$2'; using $dbformat"
		    ;;
	    esac
	    shift
	    ;;
	-v | --verbose )
	    verbose=1
	    ;;
	-z | --compress )
	    if [ "x$2" = "xnone" ] || which $2; then
		compress=$2
	    else
		warn "Compression program $2 not found; using $compress"
	    fi
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


if [ "x$1" = "x" ]; then
    error "No corpus name specified"
fi

target_corpus_root=${target_corpus_root:-$corpus_root}
pkgdir=${pkgdir:-$corpus_root/$pkgsubdir}
regdir=${regdir:-$corpus_root/$regsubdir}
datadir=${datadir:-$corpus_root/$datasubdir}
sqldir=${sqldir:-$corpus_root/$sqlsubdir}
tsvdir=${tsvdir:-$sqldir}

corpus_name=$1
shift

if [ ! -d "$regdir" ]; then
    error "Cannot access registry directory $regdir"
fi

tmp_prefix=$tmpdir/$progname.$$

eval archive_ext=\$archive_ext_$compress

if [ "x$1" = "x" ]; then
    corpus_ids=$corpus_name
else
    corpus_ids=$@
fi

(
    cd $regdir
    ls $corpus_ids > $tmp_prefix.corpora 2> $tmp_prefix.errors
)

if [ -s $tmp_prefix.errors ]; then
    error_files=`sed -e 's/^.*cannot access \([^:]*\):.*$/\1/' < $tmp_prefix.errors`
    error "Corpora not found in the CWB corpus registry: $error_files"
fi

corpus_ids=`cat $tmp_prefix.corpora`

add_prefix () {
    prefix=$1
    shift
    for arg in "$@"; do
	echo $prefix$arg
    done
}

fill_dirtempl () {
    dirtempl=$1
    corpus_id=$2
    echo "$dirtempl" |
    sed -e "s,{corpname},$corpus_name,g; s,{corpid},$corpus_id,g"
}

make_rels_table_names () {
    corp_id_upper=`echo $1 | sed -e 's/\(.*\)/\U\1\E/'`
    for base in $rels_tables_basenames; do
	echo relations_${corp_id_upper}_$base |
	sed -e 's/_@//'
    done
}

run_mysqldump () {
    extra_opts=
    while true; do
	case "$1" in
	    -* )
		extra_opts="$extra_opts $1"
		shift
		;;
	    * )
		break
		;;
	esac
    done
    mysqldump --no-autocommit $mysql_opts $extra_opts $korpdb "$@" 2> /dev/null
}

compress_or_rm_sqlfile () {
    sqlfile=$1
    if grep -q 'INSERT INTO' $sqlfile; then
	if [ "x$compress" != "xnone" ]; then
	    $compress $sqlfile
	fi
    else
	rm $sqlfile
    fi
}

make_sql_table_part () {
    corp_id=$1
    corp_id_upper=`echo $corp_id | sed -e 's/\(.*\)/\U\1\E/'`
    filetype=$2
    eval tablename=\$sql_table_name_$filetype
    if [ "x$tablename" = "x" ]; then
	tablename=$filetype
    fi
    sqlfile=`fill_dirtempl $sqldir $corp_id`/${corp_id}_$filetype.sql
    # 
    {
	# Add a CREATE TABLE IF NOT EXISTS statement for the table, so
        # that the package can be installed even on an empty database.
        # By default, mysqldump (without --no-create-info) would first
        # drop the database and then recreate it, but we need to
        # retain the data for the other corpora.
	run_mysqldump --no-data --compact $tablename |
	sed -e 's/CREATE TABLE/& IF NOT EXISTS/'
	echo
	# Instruct to delete existing data for the corpus first
	echo "DELETE FROM $tablename WHERE corpus='$corp_id_upper';"
	echo
	# The actual data dump
	run_mysqldump --no-create-info --where="corpus='$corp_id_upper'" \
	    $tablename
    } > $sqlfile
    compress_or_rm_sqlfile $sqlfile
}

dump_database () {
    corp_id=$1
    rels_tables=`make_rels_table_names $corp_id`
    sqldir_real=`fill_dirtempl $sqldir $corp_id`
    run_mysqldump $rels_tables > $sqldir_real/${corp_id}_rels.sql
    compress_or_rm_sqlfile $sqldir_real/${corp_id}_rels.sql
    for filetype in $sql_file_types_multicorpus; do
	make_sql_table_part $corp_id $filetype
    done
}

get_corpus_date () {
    (
	cd $datadir
	ls -lt --time-style=long-iso "$@" |
	grep -A1 '^total' |
	grep -E -v '^(total|--)' |
	awk '{print $6}' |
	sort -r |
	head -1 |
	tr -d '-'
    )
}

list_existing_db_files_by_type () {
    corp_id=$1
    type=$2
    db_filetype=$3
    if [ "x$type" = "xtsv" ]; then
	dir=$tsvdir
	ext=.tsv
    else
	dir=$sqldir
	ext=.sql
    fi
    dir=`fill_dirtempl $dir $corp_id`
    basename="$dir/${corp_id}_$filetype*$ext"
    ls -t $basename $basename.gz $basename.bz2 $basename.xz 2> /dev/null
}

get_first_word () {
    echo "$1"
}

list_existing_db_files () {
    corp_id=$1
    type=$2
    filenames_sql=`list_existing_db_files_by_type $corp_id $type sql`
    filenames_tsv=`list_existing_db_files_by_type $corp_id $type tsv`
    if [ "x$filenames_sql" != x ]; then
	if [ "x$filenames_tsv" != x ]; then
	    firstfile_sql=`get_first_word $filenames_sql`
	    firstfile_tsv=`get_first_word $filenames_tsv`
	    if [ "$firstfile_sql" -nt "$firstfile_tsv" ]; then
		echo "$filenames_sql"
	    else
		echo "$filenames_tsv"
	    fi
	else
	    echo "$filenames_sql"
	fi
    else
	echo "$filenames_tsv"
    fi
}

list_db_files () {
    if [ "$dbformat" != auto ]; then
	list_existing_db_files_by_type $corpus_id $dbformat
    else
	dbfiles=`list_existing_db_files $corpus_id`
	if [ "x$dbfiles" = "x" ]; then
	    dump_database $corpus_id
	    list_existing_db_files $corpus_id
	else
	    echo "$dbfiles"
	fi
    fi
}

if [ "$corpus_root" = "$target_corpus_root" ]; then
    target_regdir=$regdir
else
    target_regdir=$tmp_prefix/$regsubdir
    mkdir -p $target_regdir
    for corpus_id in $corpus_ids; do
	sed -e "s,^\(HOME\|INFO\) .*\($corpus_id\),\1 $target_corpus_root/$datasubdir/\2," $regdir/$corpus_id > $target_regdir/$corpus_id
	touch --reference=$regdir/$corpus_id $target_regdir/$corpus_id
    done
fi

corpus_files=
for corpus_id in $corpus_ids; do
    corpus_files="$corpus_files $target_regdir/$corpus_id $datadir/$corpus_id "`list_db_files $corpus_id`
done

corpus_date=`get_corpus_date $corpus_ids`
mkdir -p $pkgdir/$corpus_name
archive_basename=${corpus_name}_korp_$corpus_date
archive_name=$pkgdir/$corpus_name/$archive_basename.$archive_ext

tar_compress_opt=
if [ "x$compress" != "xnone" ]; then
    tar_compress_opt=--use-compress-program=$compress
fi

remove_leading_slash () {
    echo "$1" | sed -e 's,^/,,'
}

transform_dirtempl () {
    remove_leading_slash "$1" |
    sed -e 's,{corp.*},[^/]*,'
}

datadir_nosl=`remove_leading_slash $datadir`
regdir_nosl=`remove_leading_slash $target_regdir`
sqldir_nosl=`transform_dirtempl $sqldir`
tsvdir_nosl=`transform_dirtempl $tsvdir`

tar cvp --group=$filegroup --mode=g+rwX,o+rX $tar_compress_opt \
    -f $archive_name --exclude-backups \
    --transform "s,^$datadir_nosl,$archive_basename/data," \
    --transform "s,^$regdir_nosl,$archive_basename/registry," \
    --transform "s,^$sqldir_nosl,$archive_basename/sql," \
    --transform "s,^$tsvdir_nosl,$archive_basename/sql," \
    --show-transformed-names $corpus_files 

chgrp $filegroup $archive_name
chmod 444 $archive_name
