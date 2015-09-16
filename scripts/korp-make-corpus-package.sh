#! /bin/bash
# -*- coding: utf-8 -*-

# Make a Korp corpus installation and archive package from CWB corpus
# files and Korp MySQL database information

# TODO:
# - Check that the CWB data files include all the necessary indices
#   produced by cwb-make. Possibly also other sanity checks for the
#   corpus.
# - Working --verbose (or --quiet).
# - Update MySQL dumps if older than the database files (or if an
#   option is specified).
# - Also include data for table auth_license in korp_auth: maybe add
#   the data (as TSV) based on an option specifying the licence -
#   category.
#
# FIXME:
# - If a --doc-dir or --script-dir is specified multiple times or
#   after a --doc-file or --script-file, the latter (probably?)
#   overwrites the former when extracting the archive. We should at
#   least warn about this.
# - Finding the most recent database files from either SQL or TSV
#   files does not work correctly; see FIXME comments in the code.


progname=`basename $0`
progdir=`dirname $0`

shortopts="hc:p:r:s:t:f:vz:"
longopts="help,corpus-root:,target-corpus-root:,package-dir:,registry:,sql-dir:,tsv-dir:,set-info:,info-from-file:,readme-file:,doc-dir:,doc-file:,script-dir:,script-file:,extra-dir:,extra-file:,database-format:,compress:,verbose"

. $progdir/korp-lib.sh

# These will be set later based on $corpus_root, which may be modified
# by options
target_corpus_root=$TARGET_CORPUS_ROOT
regdir=$CORPUS_REGISTRY
datadir=$CORPUS_DATADIR
sqldir=$CORPUS_SQLDIR
pkgdir=$CORPUS_PKGDIR
tsvdir=$CORPUS_TSVDIR
tmpdir=${TMPDIR:-${TEMPDIR:-${TMP:-${TEMP:-/tmp}}}}

cwbdata_extract_info=$progdir/cwbdata-extract-info.sh

regsubdir=registry
datasubdir=data
sqlsubdir=sql
pkgsubdir=pkgs

compress=gzip
verbose=
dbformat=auto

exclude_files="backup *~ *.bak *.bak[0-9] *.old *.old[0-9] *.prev *.prev[0-9]"

has_readme=
has_docs=
has_scripts=

archive_ext_none=tar
archive_ext_gzip=tgz
archive_ext_bzip=tbz
archive_ext_xz=txz

sql_file_types="lemgrams rels timespans"
sql_file_types_multicorpus="lemgrams timespans"
sql_table_name_lemgrams=lemgram_index
rels_tables_basenames="@ rel head_rel dep_rel sentences"

extra_info_file=$tmp_prefix.info
touch $extra_info_file


usage () {
    cat <<EOF
Usage: $progname [options] corpus_name [corpus_id ...]

Make an archive package for corpus corpus_name, containing the Korp
corpora corpus_id ... (or corpus_name if corpus_id not specified).

Options:
  -h, --help      show this help
  -c, --corpus-root DIR
                  use DIR as the root directory of corpus files for the
                  source files (CORPUS_ROOT) (default: $corpus_root)
  --target-corpus-root DIR
                  use DIR as the root directory of corpus files for the
                  target files (to adjust paths in the corpus registry files)
                  (default: CORPUS_ROOT)
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
  --set-info KEY:VALUE
                  set the corpus information item KEY (in the file .info) to
                  the value VALUE, where KEY is of the form [SECTION_]SUBITEM,
                  where SECTION can be "Metadata", "Licence" or "Compiler" and
                  SUBITEM "URL", "URN", "Name" or "Description"; this option
                  can be repeated multiple times
  --info-from-file FILENAME
                  read information items to be added from file FILENAME
  --readme-file FILE
                  include FILE as a top-level read-me file; the option may
                  be specified multiple times to include multiple files
  --doc-dir DIR   include DIR as a documentation directory 'doc' in the
                  package
  --doc-file FILE include FILE as a documentation file in directory 'doc';
                  may be specified multiple times
  --script-dir DIR
                  include DIR as a (conversion) script directory 'scripts' in
                  the package
  --script-file FILE
                  include FILE as a (conversion) script file in directory
                  'scripts'; may be specified multiple times
  --extra-dir SRCDIR[:DSTDIR]
                  include directory SRCDIR in the package; if :DSTDIR is
                  specified, the directory is renamed as DSTDIR in the
                  package; the option may be specified multiple times
  --extra-file SRCFILE[:DSTFILE]
                  include file SRCFILE in the package; if :DSTFILE is
                  specified, the file is renamed as DSTFILE in the
                  package; the option may be specified multiple times
  -f, --database-format FMT
                  include database files in format FMT: either sql (SQL),
                  tsv (TSV) or auto (SQL or TSV, whichever files are newer)
                  (default: $dbformat)
  -z, --compress PROG
                  compress files with PROG; "none" for no compression
                  (default: $compress)

Environment variables:
  Default values for the various directories can also be specified via
  the following environment variables: CORPUS_ROOT, TARGET_CORPUS_ROOT,
  CORPUS_PKGDIR, CORPUS_REGISTRY, CORPUS_SQLDIR, CORPUS_TSVDIR.
EOF
    exit 0
}


extra_corpus_files=
extra_dir_and_file_transforms=

remove_leading_slash () {
    echo "$1" | sed -e 's,^/,,'
}

add_extra_dir_or_file () {
    local source=$1
    local target=$2
    if [ "x$target" = x ]; then
	case "$source" in
	    *:* )
		target=$(echo "$source" | sed -e 's/^.*://')
		source=$(echo "$source" | sed -e 's/:[^:]*$//')
		;;
	    * )
		target=$source
		;;
	esac
    fi
    extra_corpus_files="$extra_corpus_files $source"
    source=$(remove_leading_slash "$source")
    extra_dir_and_file_transforms="$extra_dir_and_file_transforms
$source $target"
}

add_extra_file () {
    local source=$1
    local target=$2
    if [ "x$target" != x ]; then
	local targetdir=$target
	if [ "$targetdir" = / ]; then
	    targetdir=
	fi
	local target="$targetdir/$(echo "$source" | sed -e 's,^.*/,,')"
    fi
    add_extra_dir_or_file "$source" "$target"
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
	--set-info )
	    printf "%s\n" "$2" >> $extra_info_file
	    shift
	    ;;
	--info-from-file )
	    cat "$2" >> $extra_info_file
	    shift
	    ;;
	--readme-file )
	    add_extra_file "$2" /
	    has_readme=1
	    shift
	    ;;
	--doc-dir )
	    add_extra_dir_or_file "$2" doc/
	    has_docs=1
	    shift
	    ;;
	--doc-file )
	    add_extra_file "$2" doc
	    has_docs=1
	    shift
	    ;;
	--script-dir )
	    add_extra_dir_or_file "$2" scripts/
	    has_scripts=1
	    shift
	    ;;
	--script-file )
	    add_extra_file "$2" scripts
	    has_scripts=1
	    shift
	    ;;
	--extra-dir )
	    add_extra_dir_or_file "$2"
	    shift
	    ;;
	--extra-file )
	    add_extra_file "$2"
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

eval archive_ext=\$archive_ext_$compress

if [ "x$1" = "x" ]; then
    corpus_ids=$corpus_name
else
    corpus_ids=$@
fi

(
    cd $regdir
    ls $corpus_ids 2> $tmp_prefix.errors |
    grep '^[a-z_][a-z0-9_-]*$' > $tmp_prefix.corpora
)

if [ -s $tmp_prefix.errors ]; then
    error_files=`sed -e 's/^.*cannot access \([^:]*\):.*$/\1/' < $tmp_prefix.errors`
    error "Corpora not found in the CWB corpus registry: $error_files"
fi

corpus_ids=`cat $tmp_prefix.corpora`

if [ "x$has_readme" = x ]; then
    warn "No readme file included"
fi
if [ "x$has_docs" = x ]; then
    warn "No documentation included"
fi
if [ "x$has_scripts" = x ]; then
    warn "No conversion scripts included"
fi


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

# FIXME: list_existing_db_files_by_type, list_existing_db_files and
# list_db_files probably do not work as they were intended to. There
# should probably be a loop somewhere iterating over the different
# types of tables.

list_existing_db_files_by_type () {
    # FIXME: Check the arguments and their use!
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
    # FIXME: Should the line below have $db_filetype instead of
    # $filetype? Now this lists all files beginning with $corp_id and
    # ending in $ext, which is probably why all this seems to work.
    basename="$dir/${corp_id}_$filetype*$ext"
    ls -t $basename $basename.gz $basename.bz2 $basename.xz 2> /dev/null
}

get_first_word () {
    echo "$1"
}

list_existing_db_files () {
    # FIXME: Check the arguments and their use!
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

corpus_files=$extra_corpus_files
for corpus_id in $corpus_ids; do
    corpus_files="$corpus_files $target_regdir/$corpus_id $datadir/$corpus_id "`list_db_files $corpus_id`
done

$cwbdata_extract_info --update --registry "$regdir" --data-root-dir "$datadir" \
    --info-from-file "$extra_info_file" $corpus_ids

corpus_date=`get_corpus_date $corpus_ids`
mkdir -p $pkgdir/$corpus_name
archive_basename=${corpus_name}_korp_$corpus_date
archive_name=$pkgdir/$corpus_name/$archive_basename.$archive_ext
archive_num=0
while [ -e $archive_name ]; do
    archive_num=`expr $archive_num + 1`
    archive_name=$pkgdir/$corpus_name/$archive_basename-`printf %02d $archive_num`.$archive_ext
done

tar_compress_opt=
if [ "x$compress" != "xnone" ]; then
    tar_compress_opt=--use-compress-program=$compress
fi

transform_dirtempl () {
    remove_leading_slash "$1" |
    sed -e 's,{corp.*},[^/]*,'
}

make_tar_transforms () {
    echo "$1" |
    while read source target; do
	echo --transform "s,^$source,$archive_basename/$target,"
    done
}

make_tar_excludes () {
    for patt in "$@"; do
	echo --exclude "$patt"
    done
}

dir_transforms=\
"$(remove_leading_slash $datadir) data
$(remove_leading_slash $target_regdir) registry
$(transform_dirtempl $sqldir) sql
$(transform_dirtempl $tsvdir) sql"
if [ "x$extra_dir_and_file_transforms" != x ]; then
    dir_transforms="$dir_transforms$extra_dir_and_file_transforms"
fi

tar cvp --group=$filegroup --mode=g+rwX,o+rX $tar_compress_opt \
    -f $archive_name --exclude-backups $(make_tar_excludes $exclude_files) \
    $(make_tar_transforms "$dir_transforms") \
    --show-transformed-names $corpus_files 

chgrp $filegroup $archive_name
chmod 444 $archive_name

echo "
Created corpus package $archive_name"
