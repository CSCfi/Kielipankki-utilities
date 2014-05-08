#! /bin/sh
# -*- coding: utf-8 -*-

# Extract from or update the information to be written to the .info
# file of a Corpus Workbench corpus (or a list of corpora): the total
# number of sentences and the date of the last update.
#
# Usage: cwbdata-extract-info [options] [corpus ... | --all] [> .info]


progname=`basename $0`

# TODO: Add options and/or environment variables for specifying these
# directories
CWB_BINDIR=/usr/local/cwb/bin
CWB_REGDIR=/v/corpora/registry
TMPDIR=/tmp

update=
verbose=
test=
all_corpora=

if which wdiff > /dev/null; then
    wdiff=wdiff
else
    wdiff=diff
fi

warn () {
    echo "$progname: Warning: $1" > /dev/stderr
}

echo_verb () {
    if [ "x$verbose" != "x" ]; then
	echo "$@"
    fi
}


usage () {
    cat <<EOF
Usage: $progname [options] [corpus ... | --all] [> .info]

Extract from or update the information to be written to the .info file
of a Corpus Workbench corpus (or a list of corpora): the total number
of sentences and the date of the last update.

Options:
  -h, --help      show this help
  -u, --update    update the .info files for the corpora if needed
  -v, --verbose   show information about the processed corpora
  -t, --test      test whether the .info files need updating
  -A, --all       process all corpora in the CWB corpus registry
EOF
    exit 0
}


# Test if GNU getopt
getopt -T > /dev/null
if [ $? -eq 4 ]; then
    # This requires GNU getopt
    args=`getopt -o "huvtA" -l "help,update,verbose,test,all" -n "$progname" -- "$@"`
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
	-u | --update )
	    update=1
	    ;;
	-v | --verbose )
	    verbose=1
	    ;;
	-t | --test )
	    test=1
	    update=1
	    ;;
	-A | --all )
	    all_corpora=1
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


get_corpus_dir () {
    corpname=$1
    echo `
    $CWB_BINDIR/cwb-describe-corpus -r "$CWB_REGDIR" $corpname |
    grep '^home directory' |
    sed -e 's/.*: //'`
}

get_all_corpora () {
    ls "$CWB_REGDIR" |
    grep -E '^[a-z_-]+$'
}

extract_info () {
    corpdir=$1
    corpname=$2
    sentcount=`
    $CWB_BINDIR/cwb-describe-corpus -r "$CWB_REGDIR" -s $corpname |
    grep -E 's-ATT sentence +' |
    sed -e 's/.* \([0-9][0-9]*\) .*/\1/'`
    updated=`
    ls -lt --time-style=long-iso "$corpdir" |
    head -2 |
    tail -1 |
    awk '{print $6}'`
    echo "Sentences: $sentcount"
    echo "Updated: $updated"
}

tmpfile=$TMPDIR/$progname.$$.tmp

if [ "x$all_corpora" != "x" ]; then
    corpora=`get_all_corpora`
else
    corpora="$@"
fi

for corpus in $corpora; do
    corpdir=`get_corpus_dir $corpus`
    if [ "x$update" = "x" ]; then
	echo_verb $corpus:
	extract_info $corpdir $corpus
    else
	extract_info $corpdir $corpus > $tmpfile
	outfile=$corpdir/.info
	if [ -e $outfile ] && cmp -s $tmpfile $outfile; then
	    echo_verb "$corpus up to date"
	else
	    if [ "x$test" != "x" ]; then
		echo "$corpus outdated"
		if [ "x$verbose" != "x" ]; then
		    $wdiff $outfile $tmpfile
		fi
	    else
		cp -p $tmpfile $outfile
		echo_verb "$corpus updated"
	    fi
	fi
    fi
done

if [ -e $tmpfile ]; then
    rm $tmpfile
fi
