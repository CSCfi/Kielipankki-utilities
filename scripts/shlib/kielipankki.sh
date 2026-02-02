# -*- coding: utf-8 -*-

# shlib/kielipankki.sh
#
# Library functions and initialization code for Bourne shell scripts:
# specific to Kielipankki (The Language Bank of Finland)
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# Load shlib components for the functions used
shlib_required_libs="msgs file str mysql"
. $_shlibdir/loadlibs.sh


# Functions

# make_licence_type licence_type
#
# Check licence_type and output it normalized (upper-case except
# "ACA-Fi"). If licence_type is not among the allowed ones, exit with
# an error message.
make_licence_type () {
    local lic_type
    lic_type=$(toupper $1)
    case $lic_type in
	PUB | ACA | ACA-FI | RES )
	    :
	    ;;
	* )
	    error "Please use licence type PUB, ACA, ACA-Fi or RES."
	    ;;
    esac
    if [ "x$lic_type" = "xACA-FI" ]; then
	lic_type=ACA-Fi
    fi
    echo $lic_type
}

# make_lbr_id lbr_id
#
# Check the form of lbr_id and output it normalized, with the
# Kielipankki URN prefix and the suffix "@LBR". If lbr_id is not of
# the required format, exit with an error message.
make_lbr_id () {
    local id prefix d
    id=$1
    if [ "$id" = "${id#$urn_prefix}" ]; then
	id="$urn_prefix$id"
    fi
    d=[0-9]
    prefix=${urn_prefix}20[1-9][0-9][01][0-9]$d$d$d
    case ${id%@LBR} in
	$prefix | ${prefix}$d | ${prefix}$d$d )
	    :
	    ;;
	* )
	    error "LBR id must be of the form [$urn_prefix]YYYYMMNNN[@LBR], where YYYYMM is year and month and NNN 3 to 5 digits"
	    ;;
    esac
    if [ "$id" = "${id%@LBR}" ]; then
	id="$id@LBR"
    fi
    echo $id
}


# _get_auth_info [--tsv-dir tsv_dir] [--sql-dir sql_dir] corpus_id
#                table_name value_column_name value_column_num
#
# Get the value of an authorization info item for corpus corpus_id
# from the Korp auth database, either from data exported to TSV or
# dumped to SQL or directly using the mysql client. table_name is the
# SQL table name (and part of the TSV filename, without the "auth_"
# prefix) with the information, value_column_name the name of the
# column containing the information and value_column_num its number.
# If --tsv-dir is specified, check TSV files in tsv_dir, otherwise in
# the default TSV directory; likewise for --sql-dir. If no TSV file
# exists, try to get the information from an SQL file; if no SQL file
# exists, try to get the information from the korp_auth MySQL database
# if accessible.
_get_auth_info () {
    local tsv_dir sql_dir corpus_id table_name value_colname value_colnum \
          tsv_file sql_file middir corpus_u
    while [ "$1" != "${1#--}" ]; do
        if [ "$1" = "--tsv-dir" ]; then
            # Explicit TSV dir
            tsv_dir=$1
            shift 2
        elif [ "$1" = "--sql-dir" ]; then
            # Explicit SQL dir
            sql_dir=$1
            shift 2
        else
            lib_error "Unknown option to _get_auth_info: $1"
        fi
    done
    corpus_id=$1
    table_name=$2
    value_colname=$3
    value_colnum=$4
    corpus_u=$(toupper $corpus_id)
    if [ "x$tsv_dir" != x ]; then
        tsv_file=$(newest_file "$tsv_dir/${corpus_id}_auth_$table_name".tsv*)
    else
        # Default TSV dir: first try .../vrt/..., then .../sql/... if
        # needed
        for middir in vrt sql; do
            tsv_dir=$corpus_root/$middir/$corpus_id
            if [ -d "$tsv_dir" ]; then
                tsv_file=$(
                    newest_file "$tsv_dir/${corpus_id}_auth_$table_name".tsv*)
            fi
            if [ "x$tsv_file" != x ]; then
                break
            fi
        done
    fi
    if [ "x$tsv_file" != x ]; then
        comprcat "$tsv_file" | head -1 | cut -f$value_colnum
    else
        if [ "x$sql_dir" = x ]; then
            # Default SQL dir
            sql_dir=$corpus_root/sql/$corpus_id
        fi
        sql_file=$(newest_file "$sql_dir/${corpus_id}_auth".sql*)
        if [ "x$sql_file" != x ]; then
            # Find the values line after the INSERT, split it into
            # columns and choose the right one; this assumes that the
            # values do not contain any of the characters ' , ( ) ;
            comprcat "$sql_file" |
                grep -A1 "INSERT INTO \`auth_$table_name\` VALUES" |
                tail -1 |
                sed -e "s/','/\t/g; s/['();]//g" |
                cut -f$value_colnum
        elif [ "x$mysql_bin" != x ]; then
            run_mysql --auth "SELECT $value_colname FROM \`auth_$table_name\` WHERE corpus='$corpus_u';" --skip-column-names
        fi
    fi
}

# get_licence_type [--tsv-dir tsv_dir] [--sql-dir sql_dir] corpus_id
#
# Get the licence type of corpus corpus_id from the Korp auth
# database. If --tsv-dir is specified, check TSV files in tsv_dir,
# otherwise in the default TSV directory; likewise for --sql-dir. If
# no TSV file exists, try to get the information from an SQL file; if
# no SQL file exists, try to get the information from the korp_auth
# MySQL database if accessible.
get_licence_type () {
    _get_auth_info "$@" license license 2
}

# get_lbr_id [--tsv-dir tsv_dir] [--sql-dir sql_dir] corpus_id
#
# Get the LBR id of corpus corpus_id from the Korp auth database. If
# --tsv-dir is specified, check TSV files in tsv_dir, otherwise in the
# default TSV directory; likewise for --sql-dir. If no TSV file
# exists, try to get the information from an SQL file; if no SQL file
# exists, try to get the information from the korp_auth MySQL database
# if accessible.
get_lbr_id () {
    _get_auth_info "$@" lbr_map lbr_id 1
}


# Variable initialization

# Kielipankki URN prefix
urn_prefix=urn:nbn:fi:lb-
