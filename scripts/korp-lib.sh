# -*- coding: utf-8 -*-

# Functions and other code common to several Bourne shell scripts
# related to Korp corpus import


# Common functions

find_existing_dir () {
    _test=$1
    _file=$2
    shift 2
    for dir in "$@"; do
	if [ $_test $dir/$_file ]; then
	    echo $dir
	    break
	fi
    done
}

find_filegroup () {
    filegroup=
    for grp in $@; do
	if groups | grep -qw $grp; then
	    filegroup=$grp
	    break
	fi
    done
    if [ "x$filegroup" = x ]; then
	filegroup=`groups | cut -d' ' -f1`
    fi
}

ensure_perms () {
    chgrp -R $filegroup "$@"
    chmod -R g+rwX "$@"
}

warn () {
    echo "$progname: Warning: $1" >&2
}

error () {
    echo "$progname: $1" >&2
    exit 1
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


toupper () {
    echo "$1" |
    sed -e 's/\(.*\)/\U\1\E/'
}



# Common initialization code

default_corpus_roots="/v/corpora /proj/clarin/korp/corpora $WRKDIR/corpora /wrk/jyniemi/corpora"

# Root directory, relative to which the corpus directory resides
corpus_root=${CORPUS_ROOT:-$(find_existing_dir -d "" $default_corpus_roots)}

default_filegroups="korp clarin"
find_filegroup $default_filegroups

tmpdir=${TMPDIR:-${TEMPDIR:-${TMP:-${TEMP:-/tmp}}}}
tmp_prefix=$tmpdir/$progname

# Korp MySQL database
korpdb=korp
# Unless specified via environment variables, assume that the Korp
# MySQL database user and password are specified in a MySQL option
# file
mysql_opts=
if [ "x$KORP_MYSQL_USER" != "x" ]; then
    mysql_opts=--user=$KORP_MYSQL_USER
fi
if [ "x$KORP_MYSQL_PASSWORD" != "x" ]; then
    mysql_opts="$mysql_opts --password=$KORP_MYSQL_PASSWORD"
fi


trap cleanup 0
trap cleanup_abort 1 2 13 15


if [ "x$shortopts" != x ]; then
    shortopts="-o $shortopts"
fi
if [ "x$longopts" != x ]; then
    longopts="-l $longopts"
fi

# Test if GNU getopt
getopt -T > /dev/null
if [ $? -eq 4 ]; then
    # This requires GNU getopt
    args=`getopt $shortopts $longopts -n "$progname" -- "$@"`
    if [ $? -ne 0 ]; then
	exit 1
    fi
    eval set -- "$args"
fi
# If not GNU getopt, arguments of long options must be separated from
# the option string by a space; getopt allows an equals sign.
