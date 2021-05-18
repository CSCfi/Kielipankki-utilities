#! /bin/bash
# -*- coding: utf-8 -*-

# Make a Korp corpus installation and archive package from CWB corpus
# files and Korp MySQL database information

# TODO:
# - Include possible fulltext files, and modify korp-install-corpora
#   to install them.
# - Check that the CWB data files include all the necessary indices
#   produced by cwb-make. Possibly also other sanity checks for the
#   corpus.
# - Working --verbose (or --quiet).
# - Update MySQL dumps if older than the database files (or if an
#   option is specified).
# - An option to generate MySQL dumps from the database, complementary
#   to the --export-database.
# - --export-database: Generate TSV files only if they do not exist or
#   if they are older than corpus data files.
# - An option to generate both a CWB data package and a VRT package
#   with a single command.
#
# FIXME:
# - Finding the most recent database files from either SQL or TSV
#   files does not work correctly; see FIXME comments in the code.
# - {corpid} does not work in the filename part of an extra VRT file.
# - Directory name transformation does not seem to work for ../dir.
# - If the TSV or SQL directory contains files for the same table
#   compressed with different programs, they are all included, instead
#   of only the newest ones.


progname=`basename $0`
progdir=`dirname $0`

usage_header="Usage: $progname [options] corpus_name [corpus_id ...]

Make an archive package for corpus corpus_name, containing the Korp
corpora corpus_id ... (or corpus_name if corpus_id not specified).
corpus_id may contain shell wildcards, in which case all matching
corpora in the corpus registry are included."

optspecs='
@ Directory options

c|corpus-root=DIR "$corpus_root" { set_corpus_root "$1" }
    use DIR as the root directory of corpus files for the source files
    (CORPUS_ROOT)
target-corpus-root=DIR "CORPUS_ROOT"
    use DIR as the root directory of corpus files for the target files
    (to adjust paths in the corpus registry files)
p|package-dir=DIR "CORPUS_ROOT/$pkgsubdir" pkgdir
    put the resulting package to a subdirectory CORPUS_NAME under the
    directory DIR
r|registry=DIR "CORPUS_ROOT/$regsubdir" { set_corpus_registry "$1" }
    use DIR as the CWB registry
s|sql-dir=DIRTEMPL "CORPUS_ROOT/$sqlsubdir/{corpid}" sqldir
    use DIRTEMPL as the source directory template for Korp MySQL
    dumps; DIRTEMPL is a directory name possibly containing
    placeholder {corpname} for corpus name or {corpid} for corpus id
t|tsv-dir=DIRTEMPL "CORPUS_ROOT/$tsvsubdir/{corpid}" tsvdir
    use DIRTEMPL as the source directory template for Korp MySQL TSV
    data files
korp-frontend-dir=DIR "$korp_frontend_dir" { set_korp_frontend_dir "$1" }
    read Korp configuration files from DIR

@ Options for VRT files

vrt-dir=DIRTEMPL "CORPUS_ROOT/$vrtsubdir/{corpid}" \
  { include_vrtdir=1; vrtdir=$1 }
    use DIRTEMPL as the source directory template for VRT files
    (*.vrt, *.vrt.*)
include-vrt-dir include_vrtdir
    include the files in the (default) VRT directory in the package;
    this option needs to be specified only if using the default VRT
    directory
vrt-file=FILE * { include_vrt=1; add_extra_file "$1" vrt/{corpid}/ }
    include FILE as a VRT file in directory "vrt/{corpname}" (or
    ("vrt/{corpid}" if the directory component of FILE contains
    {corpid}) in the package; this option may be specified multiple
    times, and FILE may contain shell wildcards
generate-vrt
    generate a single VRT file for each corpus from the CWB corpus
    data; include the file in the package but do not add it to the VRT
    directory
update-vrt|generate-missing-vrt { update_vrt=1; include_vrtdir=1; }
    update or generate a single VRT file from the CWB corpus data for
    each corpus for which it is missing from the VRT directory or is
    older than the CWB data of the corpus, and include the file in the
    package
no-cwb-data omit_cwb_data
    omit CWB data files from the package; this option requires
    that VRT files are being included in the package

@ Options for corpus information

licence-type=LIC auth_opts { add_auth_opts licence_type $optname $1 }
    set the corpus licence type to LIC, where LIC is one of PUB, ACA,
    ACA-Fi or RES
lbr-id=URN { add_auth_opts lbr_id $optname $1 }
    set the LBR id of the corpus to URN, which is of the form
    [urn:nbn:fi:lb-]YYYYMMNNN[@LBR], where YYYYMM is year and month
    and NNN 3 to 5 digits; the bracketed parts are added if left out
set-info=KEY:VALUE * { printf "%s\n" "$1" >> "$extra_info_file" }
    set the corpus information item KEY (in the file .info) to the
    value VALUE, where KEY is of the form [SECTION_]SUBITEM, where
    SECTION can be "Metadata", "Licence" or "Compiler" and SUBITEM
    "URL", "URN", "Name" or "Description"; this option can be repeated
    multiple times
info-from-file=FILENAME { cat "$1" >> "$extra_info_file" }
    read information items to be added from file FILENAME

@ Options for additional files

readme-file=FILE * { add_extra_file --prepend "$1" /; has_readme=1 }
    include FILE as a top-level read-me file; the option may be
    specified multiple times to include multiple files, and FILE may
    contain shell wildcards (but braces are not expanded)
doc-dir=DIR { add_extra_dir "$1" doc/; has_docs=1 }
    include DIR as a documentation directory "doc" in the package
doc-file=FILE * { add_extra_file "$1" doc/; has_docs=1 }
    include FILE as a documentation file in directory "doc"; may be
    specified multiple times, and FILE may contain shell wildcards
script-dir=DIR { add_extra_dir "$1" scripts/; has_scripts=1 }
    include DIR as a (conversion) script directory "scripts" in the
    package
script-file=FILE * { add_extra_file "$1" scripts/; has_scripts=1}
    include FILE as a (conversion) script file in directory "scripts";
    may be specified multiple times, and FILE may contain shell
    wildcards
extra-dir=SRCDIR[:DSTDIR] * { add_extra_dir "$1" }
    include directory SRCDIR in the package; if :DSTDIR is specified,
    the directory is renamed as DSTDIR in the package; the option may
    be specified multiple times
extra-file=SRCFILE[:DSTFILE] * { add_extra_file "$1" }
    include file SRCFILE in the package; if :DSTFILE is specified, the
    file is renamed as DSTFILE in the package; if DSTFILE ends in a
    slash or if SRCFILE contains wildcards, DSTFILE is considered a
    directory name and SRCFILE is placed in that directory in the
    package; the option may be specified multiple times

@ Options controlling the output

f|database-format=FMT "auto" dbformat { set_db_format "$1" }
    include database files in format FMT: either sql (SQL), tsv (TSV),
    auto (SQL or TSV, whichever files are newer) or none (do not
    include database files)
export-database export_db { export_db=1; set_db_format "tsv" }
    export database data into TSV files to be packaged; implies
   --database-format=tsv
z|compress=PROG "gzip" { set_compress "$1" }
    compress files with PROG; "none" for no compression
'

usage_footer="Environment variables:
  Default values for the various directories can also be specified via
  the following environment variables: CORPUS_ROOT, TARGET_CORPUS_ROOT,
  CORPUS_PKGDIR, CORPUS_REGISTRY, CORPUS_SQLDIR, CORPUS_TSVDIR, CORPUS_VRTDIR,
  KORP_FRONTEND_DIR."


. $progdir/korp-lib.sh


# Uncomment to enable some debug output to stderr:
# debug=1

# These will be set later based on $corpus_root, which may be modified
# by options
target_corpus_root=$TARGET_CORPUS_ROOT
regdir=$CORPUS_REGISTRY
datadir=$CORPUS_DATADIR
sqldir=$CORPUS_SQLDIR
pkgdir=$CORPUS_PKGDIR
tsvdir=$CORPUS_TSVDIR
vrtdir=$CORPUS_VRTDIR

cwbdata_extract_info=$progdir/cwbdata-extract-info.sh
cwbdata2vrt=$progdir/cwbdata2vrt-simple.sh
korp_mysql_export="$progdir/korp-mysql-export.sh"
korp_make_auth_info=$progdir/korp-make-auth-info.sh

regsubdir=registry
datasubdir=data
sqlsubdir=sql
tsvsubdir=vrt
pkgsubdir=pkgs
vrtsubdir=vrt

include_vrt=

exclude_files="backup *~ *.bak *.bak[0-9] *.old *.old[0-9] *.prev *.prev[0-9]"

has_readme=
has_docs=
has_scripts=

archive_ext_none=tar
archive_ext_gzip=tgz
archive_ext_bzip2=tbz
archive_ext_xz=txz

archive_type_name=korp

sql_file_types="lemgrams rels timespans timedata timedata_date"
sql_file_types_multicorpus="lemgrams timespans timedata timedata_date"
sql_table_name_lemgrams=lemgram_index
rels_tables_basenames="@ rel head_rel dep_rel strings sentences"

frontend_config_files="config.js $(echo modes/{other_languages,parallel,swedish}_mode.js) translations/corpora-*.json"

extra_info_file=$tmp_prefix.info
touch $extra_info_file

corpus_files=
corpus_files_prepend=
extra_dir_and_file_transforms=


# Functions used in the option handler (directly or indirectly)

remove_leading_slash () {
    printf '%s\n' "$1" | sed -e 's,^/*,,'
}

remove_trailing_slash () {
    printf '%s\n' "$1" | sed -e 's,/*$,,'
}

dirname_slash () {
    # dirname drops the last component even with a trailing slash, so
    # add a @ to mark the file name after a slash. If the argument has
    # no trailing slash, this works like dirname.
    dirname "$1@"
}

is_dirname () {
    case "$1" in
	*/ )
	    return 0
	    ;;
    esac
    return 1
}

add_transform () {
    echo_dbg add_transform "$1" "$2"
    extra_dir_and_file_transforms="$extra_dir_and_file_transforms
$1 $2"
}

add_corpus_files () {
    local prepend any any_added _fname
    # If --prepend is specified, prepend the file name to
    # $corpus_files instead of appending.
    prepend=
    if [ "x$1" = "x--prepend" ]; then
        prepend=1
        shift
    fi
    # If --any is specified, warn on non-existent files only if none
    # of the files specified as arguments is found.
    if [ "x$1" = "x--any" ]; then
	any=1
	shift
    fi
    for _fname in "$@"; do
	if ls $_fname > /dev/null 2>&1; then
            if [ "x$prepend" != x ]; then
                corpus_files_prepend="$corpus_files_prepend $_fname"
            else
	        corpus_files="$corpus_files $_fname"
            fi
	    any_added=1
	elif [ "x$any" = x ]; then
	    warn "File or directory not found: $_fname"
	fi
    done
    if [ "x$any" != x ] &&  [ "x$any_added" = x ]; then
	warn "None of the files or directories found: $*"
    fi
}

add_corpus_files_expand () {
    # Add corpus files with "{corp}" in arguments expanded to each
    # corpus id in turn
    local fname corpus_id
    for fname in "$@"; do
        if [[ $fname = *{corp*}* ]]; then
            for corpus_id in $corpus_ids; do
                add_corpus_files "$(echo $(fill_dirtempl $fname $corpus_id))"
            done
        else
            add_corpus_files "$(echo $fname)"
        fi
    done
}

has_wildcards () {
    # FIXME: This does not take into account backslash-protected
    # wildcards, which should not be counted as wildcards.
    case "$1" in
	*\** | *\?* | *\[* )
	    return 0
	    ;;
    esac
    return 1
}

wildcards_to_regex () {
    echo "$1" |
    sed -e 's,\.,\\.,g; s,?,[^/],g; s,\*,[^/]*,g;'
}

set_korp_frontend_dir () {
    if test_file -r $1/config.js warn \
	"config.js not found or not accessible in directory $1; using the default Korp frontend directory $korp_frontend_dir"
    then
	korp_frontend_dir=$1
    fi
}

set_db_format () {
    case "$1" in
	sql | SQL )
	    dbformat=sql
	    ;;
	tsv | TSV )
	    dbformat=tsv
	    ;;
	auto | automatic )
	    dbformat=auto
	    ;;
	none )
	    dbformat=none
	    ;;
	* )
	    warn "Invalid database format '$1'; using $dbformat"
	    ;;
    esac
}

set_compress () {
    if [ "x$1" = "xnone" ] || which $1 &> /dev/null; then
	if [ "x$1" = "xcat" ]; then
	    compress=none
	else
	    compress=$1
	fi
    else
	warn "Compression program $1 not found; using $compress"
    fi
}

add_extra_dir_or_file () {
    # Target ends in / => dir, transform the dir part of source;
    # otherwise transform the whole source; source ends in / => dir
    local prepend=
    if [ "x$1" = "x--prepend" ]; then
        prepend=$1
        shift
    fi
    local source=$1
    local target=$2
    echo_dbg "** add_extra:param" "$source" "$target"
    if [ "x$target" = x ]; then
	case "$source" in
	    *:* )
		target=$(echo "$source" | sed -e 's/^.*://')
		source=$(echo "$source" | sed -e 's/:[^:]*$//')
		# If the source contains wildcards, then the target
		# should always be a directory.
		if has_wildcards "$source"; then
		    target=$target/
		fi
		;;
	    * )
		if has_wildcards "$source"; then
		    target=$(dirname_slash "$source")/
		else
		    target=$source
		fi
		;;
	esac
    fi
    local sourcedir=$(remove_leading_slash $(dirname_slash "$source"))
    local targetdir=$(remove_leading_slash $(dirname_slash "$target"))
    echo_dbg add_extra:dirs "$sourcedir" "$targetdir"
    add_corpus_files $prepend $(remove_trailing_slash "$source")
    source=$(remove_leading_slash "$source")
    target=$(remove_leading_slash "$target")
    echo_dbg add_extra:mods "$source" "$target"
    if is_dirname "$target" || [ "x$targetdir" = x ]; then
	local targetdir_slash=
	if [ "x$targetdir" != x ]; then
	    targetdir_slash="$targetdir/"
	fi
	# Originally $targetdir = /
	if [ "x$sourcedir" = x. ]; then
	    # Extra backslashes to protect them through echos
	    add_transform "\\\\($source\\\\)" "$targetdir_slash\\\\1"
	elif is_dirname "$source"; then
	    add_transform "$sourcedir/" "$targetdir_slash"
	    # The following is now added in make_tar_transforms:
	    # add_transform "$sourcedir\$" "$targetdir"
	else
	    local sourcefile=$(wildcards_to_regex $(basename "$source"))
	    add_transform \
		"$sourcedir/\\\\($sourcefile\\\\)" "$targetdir_slash\\\\1"
	fi
    else
	add_transform "$source" "$target"
    fi
}

add_extra_file () {
    add_extra_dir_or_file "$@"
}

add_extra_dir () {
    local prepend=
    if [ "x$1" = "x--prepend" ]; then
        prepend=$1
        shift
    fi
    local target=$2
    if [ "x$target" != x ]; then
	target="$target/"
    fi
    add_extra_dir_or_file \
        $prepend "$(echo "$1" | sed -e 's,:,/:,; s,$,/,')" "$target"
}

add_auth_opts () {
    local type opt val
    type=$1
    opt=$2
    val=$3
    val=$(eval "make_$type \$val")
    exit_if_error $?
    auth_opts="$auth_opts $opt $val"
}

# Process options
eval "$optinfo_opt_handler"


if [ "x$1" = "x" ]; then
    error "No corpus name specified"
fi

target_corpus_root=${target_corpus_root:-$corpus_root}
pkgdir=${pkgdir:-$corpus_root/$pkgsubdir}
regdir=$(remove_trailing_slash $cwb_regdir)
datadir=$(remove_trailing_slash ${datadir:-$corpus_root/$datasubdir})
sqldir=$(remove_trailing_slash ${sqldir:-"$corpus_root/$sqlsubdir/{corpid}"})
tsvdir=$(remove_trailing_slash ${tsvdir:-"$corpus_root/$tsvsubdir/{corpid}"})
vrtdir=$(remove_trailing_slash ${vrtdir:-"$corpus_root/$vrtsubdir/{corpid}"})

if [ "x$include_vrtdir$generate_vrt" != "x" ]; then
    include_vrt=1
fi

corpus_name=$1
shift

if [ ! -d "$regdir" ]; then
    error "Cannot access registry directory $regdir"
fi

if [ "x$omit_cwb_data" != x ]; then
    if [ "x$include_vrt" = x ]; then
	error "You need to include VRT data when omitting CWB data."
    fi
    archive_type_name=vrt
fi

if [ "x$generate_vrt" != x ] && [ "x$update_vrt" != x ]; then
    warn "Both --generate-vrt and --update-vrt specified; assuming --update-vrt"
    generate_vrt=
fi

eval archive_ext=\$archive_ext_$compress
if [ "x$archive_ext" = x ]; then
    archive_ext=tar.$compress
    warn "Unrecognized compression program $compress: using package file name extension .$archive_ext"
fi

if [ "x$1" = "x" ]; then
    corpus_ids=$corpus_name
else
    corpus_ids="$(list_corpora "$@")"
fi

if [ "x$korp_frontend_dir" = "x" ]; then
    warn "Korp frontend directory not found"
elif test_file -r $korp_frontend_dir/config.js warn \
    "$korp_frontend_dir/config.js not found or not accessible; not including Korp configuration files";
then
    for fname_patt in $frontend_config_files; do
	add_corpus_files $(echo $korp_frontend_dir/$fname_patt)
    done
fi

if [ "x$has_readme" = x ]; then
    warn "No readme file included"
fi
if [ "x$has_docs" = x ]; then
    warn "No documentation included"
fi
if [ "x$has_scripts" = x ]; then
    warn "No conversion scripts included"
fi

generate_vrt () {
    local corpus_id=$1
    $cwbdata2vrt --all-attributes --output-file=- $corpus_id
}

if [ "x$generate_vrt" != x ]; then
    mkdir -p $tmp_prefix.vrt
    for corpus_id in $corpus_ids; do
	vrt_file=$tmp_prefix.vrt/$corpus_id.vrt
	generate_vrt $corpus_id > "$vrt_file"
	add_corpus_files "$vrt_file"
	add_transform "$vrt_file" vrt/$corpus_id/$corpus_id.vrt
    done
fi

fill_dirtempl () {
    dirtempl=$1
    corpus_id=$2
    echo "$dirtempl" |
    sed -e "s,{corpname},$corpus_name,g; s,{corpid},$corpus_id,g"
}

vrt_file_is_uptodate () {
    local corpus_id=$1
    local vrt_file=$2
    local newer_corpus_files
    vrt_file=$(ls -t "$vrt_file" "$vrt_file".* 2> /dev/null | head -1)
    if [ "x$vrt_file" = x ]; then
	return 1
    fi
    newer_corpus_files=$(
	find "$datadir"/$corpus_id -newer "$vrt_file" -name '[a-z]*')
    [ "x$newer_corpus_files" = x ]
}

if [ "x$update_vrt" != x ]; then
    for corpus_id in $corpus_ids; do
	corpus_vrtdir=$(fill_dirtempl "$vrtdir" $corpus_id)
	vrt_file=$corpus_vrtdir/$corpus_id.vrt
	mkdir -p "$corpus_vrtdir"
	if ! vrt_file_is_uptodate $corpus_id "$vrt_file"; then
	    # Would the following be safe?
	    # rm -f "$vrt_file" "vrt_file".*
	    generate_vrt $corpus_id > "$vrt_file"
	    if [ "x$compress" != "xnone" ]; then
		$compress -f "$vrt_file"
	    fi
	fi
    done
fi

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


if [ "x$auth_opts" != "x" ]; then
    $korp_make_auth_info --tsv-dir "$tsvdir" $auth_opts $corpus_ids
fi

echo_dbg extra_files "$corpus_files"
# Add the extra files to the end, except for those to be prepended
extra_corpus_files=$corpus_files
corpus_files=
add_corpus_files_expand $corpus_files_prepend
for corpus_id in $corpus_ids; do
    # Include the CWB registry file as documentation of the VRT fields
    # even if omitting CWB data
    add_corpus_files "$target_regdir/$corpus_id"
    if [ "x$omit_cwb_data" = x ]; then
	add_corpus_files "$datadir/$corpus_id"
    fi
    if [ "x$export_db" != x ]; then
	$korp_mysql_export --corpus-root "$corpus_root" \
	    --output-dir "$tsvdir" --compress "$compress" $corpus_id
    fi
    if [ "x$dbformat" != xnone ]; then
	add_corpus_files $(list_db_files $corpus_id)
    fi
    if [ "x$include_vrtdir" != x ]; then
	filepatt=$(fill_dirtempl "$vrtdir/*.vrt $vrtdir/*.vrt.*" $corpus_id)
	# --any to warn only if neither *.vrt nor *.vrt.* is found
	add_corpus_files --any $(remove_trailing_slash \
	    "$(fill_dirtempl "$vrtdir/*.vrt $vrtdir/*.vrt.*" $corpus_id)")
    fi
done
add_corpus_files_expand $extra_corpus_files
echo_dbg corpus_files "$corpus_files"

for corpus_id in $corpus_ids; do
    $cwbdata_extract_info --update --registry "$regdir" \
	--data-root-dir "$datadir" \
	--tsv-dir $(fill_dirtempl "$tsvdir" $corpus_id) \
	--info-from-file "$extra_info_file" $corpus_id
done

corpus_date=`get_corpus_date $corpus_ids`
mkdir_perms $pkgdir/$corpus_name
archive_basename=${corpus_name}_${archive_type_name}_$corpus_date
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
    # Multiple backslashes are needed in the sed expression because of
    # multiple echos, through which the output goes. (?)
    remove_leading_slash "$1" |
    sed -e 's,{corp.*},\\([^/]*\\),'
}

transform_dirtempl_pair () {
    local srcdir=$1
    local dstdir=$2
    local repl=
    case $dstdir in
	*{corp*}* )
	    dstdir=${dstdir/"{corpname}"/$corpus_name}
	    case $srcdir in
		*{corpid}* )
		    # This assumes that \1 is in the filename part,
		    # thus later than {corpid}
		    dstdir=${dstdir/'\1'/'\2'}
		    repl='\1'
		    ;;
		* )
		    repl=$corpus_name
		    ;;
	    esac
	    dstdir=${dstdir/"{corpid}"/$repl}
	    ;;
    esac
    srcdir=$(transform_dirtempl "$srcdir")
    echo "$srcdir $dstdir"
}

make_tar_transform () {
    echo --transform "s,^$1,$archive_basename/$2,"
    echo_dbg tar_transform:to "s,^$1,$archive_basename/$2,"
}

make_tar_transforms () {
    local source=
    local target=
    echo_dbg tar_transforms:param "$1"
    echo "$1" |
    sort -u |
    while read source target; do
	echo_dbg tar_transform:from "$source" "$target"
	local pair=$(transform_dirtempl_pair $source $target)
	source=${pair% *}
	target=${pair#* }
        # Tar removes leading "../" before transformations, so remove
        # it to make the transformation work
        source=${source#../}
	make_tar_transform "$source" "$target"
	if [[ "$source" = */ && "$target" = */ ]]; then
	    make_tar_transform "$(remove_trailing_slash $source)\$" \
		"$(remove_trailing_slash $target)"
	fi
    done
}

make_tar_excludes () {
    for patt in "$@"; do
	printf '%s\n' --exclude "$patt"
    done
}

dir_transforms=\
"$datadir/ data/
$target_regdir/ registry/
$sqldir/\\\\([^/]*\\\\.sql[^/]*\\\\) sql/{corpid}/\\\\1
$tsvdir/\\\\([^/]*\\\\.tsv[^/]*\\\\) sql/{corpid}/\\\\1
$vrtdir/\\\\([^/]*\\\\.vrt[^/]*\\\\) vrt/{corpid}/\\\\1"
if [ "x$korp_frontend_dir" != "x" ]; then
    dir_transforms="$dir_transforms
$korp_frontend_dir/ korp_config/"
fi
if [ "x$extra_dir_and_file_transforms" != x ]; then
    dir_transforms="$dir_transforms$extra_dir_and_file_transforms"
fi

echo_dbg "$dir_transforms"
tar cvp --group=$filegroup --mode=g+rwX,o+rX $tar_compress_opt \
    -f $archive_name --exclude-backups $(make_tar_excludes $exclude_files) \
    $(make_tar_transforms "$dir_transforms") \
    --ignore-failed-read \
    --show-transformed-names $corpus_files

chgrp $filegroup $archive_name
chmod 444 $archive_name

echo "
Created corpus package $archive_name"
