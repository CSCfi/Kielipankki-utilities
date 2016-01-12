#! /bin/sh
# -*- coding: utf-8 -*-

# Extract from or update the information to be written to the .info
# file of a Corpus Workbench corpus (or a list of corpora): the total
# number of sentences and the date of the last update.
#
# Usage: cwbdata-extract-info.sh [options] [corpus ... | --all] [> .info]
#
# For more information: cwbdata-extract-info.sh --help
#
# TODO:
# - Preserve the order of the items in the info file when updating
# - Validity checks for extra info items; maybe separate options for
#   the supported info items
# - Option to remove info items


progname=`basename $0`
progdir=`dirname $0`

shortopts="hc:r:d:s:tuvA"
longopts="help,cwbdir:,registry:,data-root-dir:,set-info:,info-from-file:,test,update,verbose,all,no-backups,backup-suffix:"

. $progdir/korp-lib.sh


cwb_regdir=${CORPUS_REGISTRY:-$corpus_root/registry}
# Use the data directory specified in the registry file of a corpus,
# unless specified via an option
data_rootdir=

update=
verbose=
test=
all_corpora=
backups=1
backup_suffix=.bak

std_info_keys_list="Sentences Updated"
std_info_keys=$(echo "$std_info_keys_list" | sed -e 's/ /|/g')

if which wdiff > /dev/null 2>&1; then
    wdiff=wdiff
else
    wdiff=diff
fi

tmp_prefix=$tmpdir/$progname.$$.tmp


usage () {
    cat <<EOF
Usage: $progname [options] [corpus ... | --all] [> .info]

Extract from or update the information to be written to the .info file
of a Corpus Workbench corpus (or a list of corpora): the total number
of sentences and the date of the last update. Corpus name arguments
may contain shell wildcards.

Options:
  -h, --help      show this help
  -c, --cwbdir DIR
                  use the CWB binaries in DIR (default: $cwb_bindir)
  -r, --registry DIR
                  use DIR as the CWB registry (default: $cwb_regdir)
  -d, --data-root-dir DIR
                  use DIR as the corpus data root directory containing the
                  corpus-specific data directories, overriding the data
                  directory specified the registry file
  -s, --set-info KEY:VALUE
                  set the information item KEY to the value VALUE, where KEY
                  is of the form [SECTION_]SUBITEM, where SECTION can be
                  "Metadata", "Licence" or "Compiler" and SUBITEM "URL",
                  "URN", "Name" or "Description"; this option can be repeated
                  multiple times
  --info-from-file FILENAME
                  read information items to be added from file FILENAME
  -t, --test      test whether the .info files need updating
  -u, --update    update the .info files for the corpora if needed
  -v, --verbose   show information about the processed corpora
  -A, --all       process all corpora in the CWB corpus registry
  --no-backups    do not make backups of the info files when updating
  --backup-suffix SUFFIX
                  use SUFFIX as the backup file suffix (default: $backup_suffix)
EOF
    exit 0
}


info_items=
info_keys=

set_info () {
    case "$1" in
	"" | "#"* )
	    return
	    ;;
    esac
    # Split the parameter using the suffix and prefix removal
    # operations of the shell. How portable is this? Apparently
    # specified by POSIX; works in at least Bash and Dash.
    _key=${1%%:*}
    _value=${1#*:}
    info_items="$info_items
$_key: $_value"
    info_keys="$info_keys|$_key"
}

read_info_file () {
    while read line; do
	set_info "$line"
    done
}


# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	-c | --cwbdir )
	    cwb_bindir=$2
	    shift
	    ;;
	-r | --registry )
	    cwb_regdir=$2
	    shift
	    ;;
	-d | --data-root-dir )
	    data_rootdir=$2
	    shift
	    ;;
	-s | --set-info )
	    set_info "$2"
	    shift
	    ;;
	--info-from-file )
	    read_info_file < "$2"
	    shift
	    ;;
	-t | --test )
	    test=1
	    update=1
	    ;;
	-u | --update )
	    update=1
	    ;;
	-v | --verbose )
	    verbose=1
	    ;;
	-A | --all )
	    all_corpora=1
	    ;;
	--no-backups )
	    backups=
	    ;;
	--backup-suffix )
	    backup_suffix=$2
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


cwb_describe_corpus=$(find_prog cwb-describe-corpus $cwb_bindir)

if [ ! -d "$cwb_regdir" ]; then
    error "Cannot access registry directory $cwb_regdir"
fi


get_corpus_dir () {
    corpname=$1
    if [ "x$data_rootdir" != x ]; then
	echo "$data_rootdir/$corpname"
    else
	echo `
	$cwb_describe_corpus -r "$cwb_regdir" $corpname |
	grep '^home directory' |
	sed -e 's/.*: //'`
    fi
}

get_sentence_count () {
    _corpname=$1
    $cwb_describe_corpus -r "$cwb_regdir" -s $_corpname |
    grep -E 's-ATT sentence +' |
    sed -e 's/.* \([0-9][0-9]*\) .*/\1/'
}

get_updated () {
    _corpdir=$1
    ls -lt --time-style=long-iso "$_corpdir" |
    head -2 |
    tail -1 |
    awk '{print $6}'
}

extract_info () {
    corpdir=$1
    corpname=$2
    sentcount=$(get_sentence_count $corpname)
    updated=$(get_updated "$corpdir")
    echo "Sentences: $sentcount"
    echo "Updated: $updated"
    if [ "x$info_items" != x ]; then
	echo "$info_items" |
	egrep -v '^$' |
	sed -e 's/: */: /'
    fi
}

infofile_tmp=$tmp_prefix.tmp

sort_info () {
    cat > $infofile_tmp
    for std_key in $std_info_keys_list; do
	egrep "^$std_key:" $infofile_tmp
    done
    egrep -v "^($std_info_keys):" $infofile_tmp |
    sort
}


infofile_old=$tmp_prefix.old
infofile_new=$tmp_prefix.new
infofile_comb=$tmp_prefix.comb

if [ "x$all_corpora" != "x" ]; then
    corpora=$(list_corpora "$cwb_regdir" "*")
else
    corpora=$(list_corpora "$cwb_regdir" $*)
fi

for corpus in $corpora; do
    if [ ! -e "$cwb_regdir/$corpus" ]; then
	warn "Corpus $corpus not found in registry $cwb_regdir"
	continue
    fi
    corpdir=`get_corpus_dir $corpus`
    if [ "x$update" = "x" ]; then
	echo_verb $corpus:
	extract_info $corpdir $corpus
    else
	extract_info $corpdir $corpus |
	sort_info > $infofile_new
	outfile=$corpdir/.info
	if [ -e $outfile ]; then
	    egrep "^($std_info_keys$info_keys):" $outfile |
	    sort_info > $infofile_old
	    if cmp -s $infofile_old $infofile_new; then
		echo_verb "$corpus up to date"
		continue
	    fi
	    if [ "x$backups" != "x" ]; then
		cp -p $outfile $outfile$backup_suffix
	    fi
	fi
	if [ "x$test" != "x" ]; then
	    echo "$corpus outdated"
	    verbose $wdiff $infofile_old $infofile_new
	else
	    {
		cat $infofile_new
		if [ -e $outfile ]; then
		    egrep -v "^($std_info_keys$info_keys):" $outfile
		fi
	    } |
	    sort_info > $infofile_comb
	    cp -p $infofile_comb $outfile
	    echo_verb "$corpus updated"
	fi
    fi
done
