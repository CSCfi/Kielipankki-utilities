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
# - --export-database=auto: Export or dump files if they exist but are
#   older than corpus data files.
# - An option to generate both a CWB data package and a VRT package
#   with a single command.
#
# FIXME:
# - {corpid} does not work in the filename part of an extra VRT file.
# - Directory name transformation does not seem to work for ../dir.
# - If the TSV or SQL directory contains files for the same table
#   compressed with different programs, they are all included, instead
#   of only the newest ones.


progname=$(basename $0)
progdir=$(dirname $0)

# A dummy variable used only in $optspecs to adjust slightly for the
# length difference of "$compress_prog" and its value, since $optspecs
# texts are wrapped based on the unexpanded value
filler=

usage_header="Usage: $progname [options] corpus_name [corpus_id ...]

Make an archive package for corpus corpus_name, containing the Korp
corpora corpus_id ... (or corpus_name if corpus_id not specified).
corpus_id may contain shell wildcards, in which case all matching
corpora in the corpus registry are included.

The package is a (compressed) tar archive whose name is in general
corpus_name_korp_yyyymmdd_hhmmss[-xx] where yyyymmdd_hhmmss is the
most recent modification date and time of the included files and xx is
a two-digit zero-padded number appended if a package without it (or
with any lower xx) already exists. With option --newer, the archive
name is slightly different; see the description of --newer below."

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

f|database-format=FMT "tsv" dbformat { set_db_format "$1" }
    include database files in format FMT: either "tsv" (TSV), "sql"
    (SQL) or "none" (omit database files)
export-database=MODE "auto" export_db { set_export_db "$1" }
    control exporting database data into TSV files or dumping into SQL
    file (depending on --database-format) to be packaged; MODE can be
    "yes" or "always" (always export), "no" or "never" (never export),
    or "auto" (export only if no database files of the chosen database
    format exist)
newer|after=DATE
    include only files whose modification date is later than DATE;
    DATE can be specified as an ISO date and time (or in any other
    format supported by GNU Tar); if DATE begins with a "/" or ".", it
    is taken to be the name of a file whose modification date is to be
    used as a reference; when using this option, the package base name
    is corpus_name_yyyymmdd_hhmmss_a_yyyymmdd_hhmmss[-xx]: the package
    contains files whose modification date is newer than ("after") the
    yyyymmdd_hhmmss following "_a_" (the other parts are as usual)
z|compress=PROG "$compress" { compress=$(get_compress "$1" "$compress") }
    compress files with PROG (one of: $compress_progs$filler);
    "none" for no compression
'

usage_footer="Environment variables:
  Default values for the various directories can also be specified via
  the following environment variables: CORPUS_ROOT, TARGET_CORPUS_ROOT,
  CORPUS_PKGDIR, CORPUS_REGISTRY, CORPUS_SQLDIR, CORPUS_TSVDIR,
  CORPUS_VRTDIR. MySQL host, username and password can be specified
  via KORP_MYSQL_HOST, KORP_MYSQL_USER and KORP_MYSQL_PASSWORD,
  respectively."


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

# Compression program
compress=gzip

exclude_files="backup *~ *.bak *.bak[0-9] *.old *.old[0-9] *.prev *.prev[0-9]"

has_readme=
has_docs=
has_scripts=

archive_ext_none=tar
archive_ext_gzip=tgz
archive_ext_bzip2=tbz
archive_ext_xz=txz

archive_type_name=korp
# The marker in a package name indicating that it contains files newer
# than the specified given date
newer_marker=a

# SQL file types (included in the SQL file name) for tables with data
# for multiple corpora
sql_file_types_multicorpus="auth lemgrams timedata timedata_date"
# All SQL file types
sql_file_types="$sql_file_types_multicorpus rels"
# sql_table_names_$type lists the names of (multi-corpus) tables from
# which data is to be included in an SQL file of $type; not required
# if $type is the same as the table name
sql_table_names_lemgrams=lemgram_index
sql_table_names_auth="auth_license auth_lbr_map"
# Base names of relations tables, where the full name is
# relations_$CORPUS_$basename ("@" denotes empty basename, with also
# the preceding underscore omitted)
rels_tables_basenames="@ rel head_rel dep_rel strings sentences"

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

set_db_format () {
    case "$1" in
        sql | SQL )
            dbformat=sql
            ;;
        tsv | TSV )
            dbformat=tsv
            ;;
        none )
            dbformat=none
            warn "Omitting database data because of --database-format=none"
            ;;
        * )
            warn "Invalid database format '$1'; using $dbformat"
            ;;
    esac
}

# Set $export_db based on $1; warn on an invalid value
set_export_db () {
    case "$1" in
        yes | always )
            export_db=yes
            ;;
        no | never )
            export_db=no
            ;;
        auto | automatic )
            export_db=auto
            ;;
        * )
            warn "Invalid value for --export-database: \"$1\"; \"using $export_db\""
            ;;
    esac
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


# Set directory variables, partly based on options
set_dirs () {
    target_corpus_root=${target_corpus_root:-$corpus_root}
    pkgdir=${pkgdir:-$corpus_root/$pkgsubdir}
    regdir=$(remove_trailing_slash $cwb_regdir)
    datadir=$(remove_trailing_slash ${datadir:-$corpus_root/$datasubdir})
    sqldir=$(remove_trailing_slash ${sqldir:-"$corpus_root/$sqlsubdir/{corpid}"})
    tsvdir=$(remove_trailing_slash ${tsvdir:-"$corpus_root/$tsvsubdir/{corpid}"})
    vrtdir=$(remove_trailing_slash ${vrtdir:-"$corpus_root/$vrtsubdir/{corpid}"})
    if [ ! -d "$regdir" ]; then
        error "Cannot access registry directory $regdir"
    fi
}

# Get CWB ids of corpora ($@) to be included and assign to $corpus_ids.
get_corpus_ids () {
    local retval
    if [ "x$1" = "x" ]; then
        # list_corpora detects non-existent corpora
        corpus_ids=$(list_corpora $corpus_name)
    else
        corpus_ids="$(list_corpora "$@")"
    fi
    # list_corpora calls function error on error but as it is run in a
    # subshell, it does not exit this script, so check the return value
    # and exit on errors
    retval=$?
    if [ $retval != 0 ]; then
        exit $retval
    fi
}

# Output the ISO date and time (at seconds precision) for the date
# passed as an argument, as returned by "date". As with tar --newer,
# if the argument begins with a "." or "/", treat it as the name of a
# file, whose last modification is output. On error, return 1 and
# output the error message from "date".
get_newer_date () {
    local indate outdate dateopt retval
    indate=$1
    # File name if begins with "." or "/"
    if [ "${indate#[./]}" != "$indate" ]; then
        dateopt=reference
    else
        dateopt=date
    fi
    outdate=$(date --$dateopt="$indate" +"%Y-%m-%d %H:%M:%S" 2>&1)
    retval=$?
    echo "$outdate"
    return $retval
}

# Check if --newer had been specified and set the values of global
# variables tar_newer_opt and newer_suff accordingly.
check_newer () {
    local date
    # tar option to create a package with files newer than specified
    tar_newer_opt=
    # File base name suffix for a package with files newer than specified
    newer_suff=
    # --newer specified, so set tar_newer_opt and newer_suff based on its
    # argument
    if [ "x$newer" != x ]; then
        date=$(get_newer_date "$newer")
        if [ $? != 0 ]; then
            error "Invalid value for --newer: ${date#date: }"
        fi
        safe_echo "Packaging only files modified after $date"
        date=${date//[:-]/}
        date=${date/ /_}
        newer_suff="_${newer_marker}_$date"
        tar_newer_opt=--newer-mtime="$newer"
    fi
}

# Check some options and set values or warn based on them.
check_options () {
    check_newer
    if [ "x$include_vrtdir$generate_vrt" != "x" ]; then
        include_vrt=1
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
        archive_ext=tar.$(get_compress_ext "$compress")
    fi
    tar_compress_opt=
    if [ "x$compress" != "xnone" ]; then
        tar_compress_opt=--use-compress-program=$compress
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
}

# Check command-line arguments and set values based on options.
# Command-line arguments left after processing options are passed as
# function arguments.
check_args () {
    if [ "x$1" = "x" ]; then
        error "No corpus name specified"
    fi
    corpus_name=$1
    shift
    set_dirs
    get_corpus_ids "$@"
    check_options
}

generate_vrt () {
    local corpus_id=$1
    $cwbdata2vrt --all-attributes --output-file=- $corpus_id
}

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

# Generate or update VRT files for all corpus ids.
generate_or_update_vrt () {
    local corpus_id vrt_file corpus_vrtdir
    if [ "x$generate_vrt" != x ]; then
        mkdir_perms $tmp_prefix.vrt
        for corpus_id in $corpus_ids; do
            vrt_file=$tmp_prefix.vrt/$corpus_id.vrt
            generate_vrt $corpus_id > "$vrt_file"
            add_corpus_files "$vrt_file"
            add_transform "$vrt_file" vrt/$corpus_id/$corpus_id.vrt
        done
    fi
    if [ "x$update_vrt" != x ]; then
        for corpus_id in $corpus_ids; do
            corpus_vrtdir=$(fill_dirtempl "$vrtdir" $corpus_id)
            vrt_file=$corpus_vrtdir/$corpus_id.vrt
            mkdir_perms "$corpus_vrtdir"
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
}

make_rels_table_names () {
    corpus_id_upper=$(echo $1 | sed -e 's/\(.*\)/\U\1\E/')
    for base in $rels_tables_basenames; do
        echo relations_${corpus_id_upper}_$base |
        sed -e 's/_@//'
    done
}

# Compress SQL file $1 with $compress, or remove it if it does not
# contain "INSERT INTO" (no data was dumped from the table).
compress_or_rm_sqlfile () {
    local sqlfile=$1
    if grep -q 'INSERT INTO' $sqlfile; then
        if [ "x$compress" != "xnone" ]; then
            # -f to overwrite possibly existing compressed file
            $compress -f $sqlfile
        fi
    else
        rm $sqlfile
    fi
}

# Dump the data for corpus with id $1 to file of type $2 where file
# type is one listed in $sql_file_types_multicorpus. If
# $sql_table_names_$2 exists, dump the tables listed in its value,
# otherwise table name is the same as file type. The output file name
# is $sqldir/$corpusid_$filetype.sql[.$compress].
make_sql_table_part () {
    local corpus_id=$1
    local corpus_id_upper=$(echo $corpus_id | sed -e 's/\(.*\)/\U\1\E/')
    local filetype=$2
    local sqlfile=$(fill_dirtempl $sqldir $corpus_id)/${corpus_id}_$filetype.sql
    local tablenames tablename
    eval tablenames=\$sql_table_names_$filetype
    if [ "x$tablenames" = "x" ]; then
        tablenames=$filetype
    fi
    {
        # Add a CREATE TABLE IF NOT EXISTS statement for the table, so
        # that the package can be installed even on an empty database.
        # By default, mysqldump (without --no-create-info) would first
        # drop the database and then recreate it, but we need to
        # retain the data for the other corpora.
        run_mysqldump --no-data --compact $tablenames |
        sed -e 's/CREATE TABLE/& IF NOT EXISTS/'
        echo
        # Instruct to delete existing data for the corpus first
        for tablename in $tablenames; do
            echo "DELETE FROM $tablename WHERE corpus='$corpus_id_upper';"
        done
        echo
        # The actual data dump
        run_mysqldump --no-create-info --where="corpus='$corpus_id_upper'" \
            $tablenames
    } > $sqlfile
    # Compress the SQL file if requested, or remove if it contains no
    # data
    compress_or_rm_sqlfile $sqlfile
}

# Dump database data for corpus id $1 by using mysqldump.
dump_database () {
    local corpus_id=$1
    local rels_tables=$(make_rels_table_names $corpus_id)
    local sqldir_real=$(fill_dirtempl $sqldir $corpus_id)
    local filetype
    mkdir_perms "$sqldir_real"
    run_mysqldump $rels_tables > $sqldir_real/${corpus_id}_rels.sql
    compress_or_rm_sqlfile $sqldir_real/${corpus_id}_rels.sql
    for filetype in $sql_file_types_multicorpus; do
        make_sql_table_part $corpus_id $filetype
    done
}

# Export database for corpus $1 to TSV or dump to SQL files, depending
# on the database format used.
export_or_dump_database () {
    local corpus_id=$1
    if [ "$dbformat" = "tsv" ]; then
        $korp_mysql_export \
            --corpus-root "$corpus_root" --output-dir "$tsvdir" \
            --compress "$compress" $corpus_id
    else
        dump_database $corpus_id
    fi
}

# Output the date (timestamp as YYYYMMMDD_hhmmss) of the most recently
# modified file of the arguments. Note that this also includes
# possibly excluded files. Directory names should end in a slash for
# the dates of the included files to be considered.
# FIXME: Make work with file names containing spaces
get_corpus_date () {
    local files newest_file
    files="$@ "
    # Append "*" after trailing slashes to get all the files in
    # directories
    files=${files/// //* }
    newest_file=$(ls -td $files | head -1)
    date --reference="$newest_file" "+%Y%m%d_%H%M%S"
}

# Output a list of existing database files for corpus with id $1 and
# type $2 ("tsv" or "sql"), most recently modified first.
list_existing_db_files_by_type () {
    local corpus_id=$1
    local type=$2
    local dir basename
    eval "dir=\$${type}dir"
    dir=$(fill_dirtempl $dir $corpus_id)
    basename="$dir/${corpus_id}_*.$type"
    ls -t $basename $basename.gz $basename.bz2 $basename.xz 2> /dev/null
}

get_first_word () {
    echo "$1"
}

# Set $dbfiles to a list of database files for corpus with id $1. If
# no database files already exist, dump the database for the corpus.
# Note that the function does not output the value of $dbfiles, as the
# function export_or_dump_database may write to stdout.
list_db_files () {
    local corpus_id=$1
    dbfiles=
    if [ "$export_db" = "yes" ]; then
        export_or_dump_database $corpus_id
    fi
    dbfiles=$(list_existing_db_files_by_type $corpus_id $dbformat)
    if [ "x$dbfiles" = "x" ]; then
        # No database files found; export them if "auto"
        if [ "$export_db" = "auto" ]; then
            export_or_dump_database $corpus_id
            dbfiles=$(list_existing_db_files_by_type $corpus_id $dbformat)
        elif [ "$export_db" = "no" ]; then
            warn "Database files not found but not exporting them because of --export-database=no"
        fi
    fi
}

# Adjust data directory in the registry file for $target_corpus_root.
process_registry () {
    local corpus_id
    if [ "$corpus_root" = "$target_corpus_root" ]; then
        target_regdir=$regdir
    else
        target_regdir=$tmp_prefix/$regsubdir
        mkdir_perms $target_regdir
        for corpus_id in $corpus_ids; do
            sed -e "s,^\(HOME\|INFO\) .*\($corpus_id\),\1 $target_corpus_root/$datasubdir/\2," $regdir/$corpus_id > $target_regdir/$corpus_id
            touch --reference=$regdir/$corpus_id $target_regdir/$corpus_id
        done
    fi
}

# Make auth info for corpora if auth options are specified.
make_auth_info () {
    if [ "x$auth_opts" != "x" ]; then
        $korp_make_auth_info --tsv-dir "$tsvdir" $auth_opts $corpus_ids
    fi
}

# Update the .info file for corpus whose id is $1.
update_info () {
    local corpus_id
    for corpus_id in $corpus_ids; do
        $cwbdata_extract_info --update --registry "$regdir" \
            --data-root-dir "$datadir" \
            --tsv-dir $(fill_dirtempl "$tsvdir" $corpus_id) \
            --info-from-file "$extra_info_file" $corpus_id
    done
}

# Add to $corpus_files the files for corpus whose id is $1.
add_single_corpus_files () {
    local corpus_id
    corpus_id=$1
    # Include the CWB registry file as documentation of the VRT fields
    # even if omitting CWB data
    add_corpus_files "$target_regdir/$corpus_id"
    if [ "x$omit_cwb_data" = x ]; then
        add_corpus_files "$datadir/$corpus_id/"
    fi
    if [ "x$dbformat" != xnone ]; then
        list_db_files $corpus_id
        add_corpus_files $dbfiles
    fi
    if [ "x$include_vrtdir" != x ]; then
        filepatt=$(fill_dirtempl "$vrtdir/*.vrt $vrtdir/*.vrt.*" $corpus_id)
        # --any to warn only if neither *.vrt nor *.vrt.* is found
        add_corpus_files --any $(remove_trailing_slash \
            "$(fill_dirtempl "$vrtdir/*.vrt $vrtdir/*.vrt.*" $corpus_id)")
    fi
}

# Add files to be included in the package to $corpus_files.
add_files () {
    local extra_corpus_files corpus_id
    generate_or_update_vrt
    process_registry
    make_auth_info
    echo_dbg extra_files "$corpus_files"
    # Add the extra files to the end, except for those to be prepended
    extra_corpus_files=$corpus_files
    corpus_files=
    add_corpus_files_expand $corpus_files_prepend
    for corpus_id in $corpus_ids; do
        add_single_corpus_files $corpus_id
    done
    add_corpus_files_expand $extra_corpus_files
    echo_dbg corpus_files "$corpus_files"
}

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

# Set archive name: $archive_name and $archive_basename.
set_archive_name () {
    local corpus_date archive_num
    corpus_date=$(get_corpus_date $corpus_files)
    mkdir_perms $pkgdir/$corpus_name
    archive_basename=${corpus_name}_${archive_type_name}_$corpus_date$newer_suff
    archive_name=$pkgdir/$corpus_name/$archive_basename.$archive_ext
    archive_num=0
    while [ -e $archive_name ]; do
        archive_num=$(($archive_num + 1))
        archive_name=$pkgdir/$corpus_name/$archive_basename-$(printf %02d $archive_num).$archive_ext
    done
}

# Output directory name transformations for tar.
make_dir_transforms () {
    local dir_transforms
    dir_transforms="$datadir/ data/
    $target_regdir/ registry/
    $sqldir/\\\\([^/]*\\\\.sql[^/]*\\\\) sql/{corpid}/\\\\1
    $tsvdir/\\\\([^/]*\\\\.tsv[^/]*\\\\) sql/{corpid}/\\\\1
    $vrtdir/\\\\([^/]*\\\\.vrt[^/]*\\\\) vrt/{corpid}/\\\\1"
    if [ "x$extra_dir_and_file_transforms" != x ]; then
        dir_transforms="$dir_transforms$extra_dir_and_file_transforms"
    fi
    echo_dbg "$dir_transforms"
    safe_echo "$dir_transforms"
}

# Create Korp corpus package.
create_package () {
    local dir_transforms
    set_archive_name
    dir_transforms="$(make_dir_transforms)"
    tar cvp --group=$filegroup --mode=g+rwX,o+rX $tar_compress_opt \
        -f $archive_name --exclude-backups $(make_tar_excludes $exclude_files) \
        $(make_tar_transforms "$dir_transforms") \
        --ignore-failed-read --sort=name \
        $tar_newer_opt \
        --show-transformed-names $corpus_files
    # Set group and permissions
    chgrp $filegroup $archive_name
    chmod a-w $archive_name
    echo "
    Created corpus package $archive_name"
}


check_args "$@"
add_files
create_package
