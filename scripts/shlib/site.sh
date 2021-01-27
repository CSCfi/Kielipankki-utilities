# -*- coding: utf-8 -*-

# shlib/site.sh
#
# Library functions and initialization code for Bourne shell scripts:
# site-specific functions and variable definitions


# Functions

get_host_env () {
    case $HOSTNAME in
	puhti* | r[0-9][0-9][cg][0-9][0-9]* | *.bullx )
	    echo puhti
	    ;;
	taito* | c[0-9] | c[0-9][0-9] | c[0-9][0-9][0-9] )
	    echo taito
	    ;;
	korp*.csc.fi | korp*.novalocal )
	    echo korp
	    ;;
	nyklait-09-01* )
	    echo nyklait-09-01
	    ;;
	* )
	    echo unknown
	    ;;
    esac
}


# Initialize variables

# Possible root directories, relative to which the corpus directory
# resides
default_corpus_roots=${default_corpus_roots:-"
    /v/corpora
    /scratch/clarin/korp/corpora
    /proj/clarin/korp/corpora
    $WRKDIR/corpora
"}

# Possible CWB binary directories
default_cwb_bindirs=${default_cwb_bindirs:-"
    /usr/local/cwb/bin
    /usr/local/bin
    /projappl/clarin/cwb/bin
    /proj/clarin/korp/cwb/bin
    $USERAPPL/bin
    /v/util/cwb/utils
"}
# Add possible CWB-Perl binary directories parallel to the CWB binary
# directories by replacing /cwb/ with /cwb-perl/.
default_cwb_bindirs="$(
    printf "%s" "$default_cwb_bindirs" |
    sed -e '/\/cwb\// {p; s/\(.*\)\/cwb\//\1\/cwb-perl\//}'
)"

default_filegroups="korp clarin"

default_korp_frontend_dirs=${default_korp_frontend_dirs:-"
    /var/www/html/korp
    /var/www/html
"}
