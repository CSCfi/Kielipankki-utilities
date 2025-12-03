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


# _get_auth_info [--tsv-dir tsv_dir] corpus_id table_name value_column_name
#                value_column_num
#
# Get the value of an authorization info item for corpus corpus_id
# from the Korp auth database, either from data exported to TSV or
# directly using the mysql client. table_name is the SQL table name
# (and part of the TSV filename, without the "auth_" prefix) with the
# information, value_column_name the name of the column containing the
# information and value_column_num its number. If --tsv-dir is
# specified, get the information from the TSV files in tsv_dir,
# otherwise in the default TSV directory. If the TSV file does not
# exist, try to get the information from the korp_auth MySQL database
# if accessible.
_get_auth_info () {
    local tsv_dir tsv_file corpus_id table_name value_colname value_colnum \
          corpus_u
    if [ "$1" = "--tsv-dir" ]; then
        # Explicit TSV dir
        tsv_dir=$1
        shift 2
        corpus_id=$1
    else
        # Default TSV dir
        corpus_id=$1
        tsv_dir=$corpus_root/vrt/$corpus_id
        if [ ! -d "$tsv_dir" ]; then
            tsv_dir=$corpus_root/sql/$corpus_id
        fi
    fi
    table_name=$2
    value_colname=$3
    value_colnum=$4
    corpus_u=$(toupper $corpus_id)
    tsv_file=$(
        ls -t "$tsv_dir/${corpus_id}_auth_$table_name".tsv* 2> /dev/null |
            head -1)
    if [ "x$tsv_file" != x ]; then
        comprcat "$tsv_file" | head -1 | cut -f$value_colnum
    elif [ "x$mysql_bin" != x ]; then
        run_mysql --auth "SELECT $value_colname FROM auth_$table_name WHERE corpus='$corpus_u';" --skip-column-names
    fi
}

# get_licence_type [--tsv-dir tsv_dir] corpus_id
#
# Get the licence type of corpus corpus_id from the Korp auth
# database. If --tsv-dir is specified, get the information from the
# TSV files in tsv_dir, otherwise in the default TSV directory. If the
# TSV file does not exist, try to get the information from the
# korp_auth MySQL database if accessible.
get_licence_type () {
    _get_auth_info "$@" license license 2
}

# get_lbr_id [--tsv-dir tsv_dir] corpus_id
#
# Get the LBR id of corpus corpus_id from the Korp auth database. If
# --tsv-dir is specified, get the information from the TSV files in
# tsv_dir, otherwise in the default TSV directory. If the TSV file
# does not exist, try to get the information from the korp_auth MySQL
# database if accessible.
get_lbr_id () {
    _get_auth_info "$@" lbr_map lbr_id 1
}


# Variable initialization

# Kielipankki URN prefix
urn_prefix=urn:nbn:fi:lb-

# The (main) Korp frontend directory
korp_frontend_dir=${KORP_FRONTEND_DIR:-$(find_existing_dir -e config.js $default_korp_frontend_dirs)}
