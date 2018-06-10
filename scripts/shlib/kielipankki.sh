# -*- coding: utf-8 -*-

# shlib/kielipankki.sh
#
# Library functions and initialization code for Bourne shell scripts:
# specific to Kielipankki (The Language Bank of Finland)
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# Load shlib components for the functions used
shlib_required_libs="msgs file str"
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


# Variable initialization

# Kielipankki URN prefix
urn_prefix=urn:nbn:fi:lb-

# The (main) Korp frontend directory
korp_frontend_dir=${KORP_FRONTEND_DIR:-$(find_existing_dir -e config.js $default_korp_frontend_dirs)}
