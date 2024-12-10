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


usage_header="Usage: $progname [options] [corpus ... | --all] [> .info]

Extract from or update the information to be written to the .info file
of a Corpus Workbench corpus (or a list of corpora): the total number
of sentences and the date of the last update. Corpus name arguments
may contain shell wildcards."

optspecs='
c|cwbdir=DIR "$cwb_bindir" cwb_bindir
    use the CWB binaries in DIR
r|registry=DIR "$cwb_regdir" cwb_regdir
    use DIR as the CWB registry
d|data-root-dir=DIR data_rootdir
    use DIR as the corpus data root directory containing the
    corpus-specific data directories, overriding the data directory
    specified the registry file
s|set-info=KEY:VALUE * { set_info "$1" }
    set the information item KEY to the value VALUE, where KEY is of
    the form [SECTION_]SUBITEM, where SECTION can be "Metadata",
    "Licence" or "Compiler" and SUBITEM "URL", "URN", "Name" or
    "Description"; this option can be repeated multiple times
info-from-file=FILENAME { read_info_file < "$1" }
    read information items to be added from file FILENAME
tsv-dir=DIR tsvdir
    extract FirstDate and LastDate information from
    DIR/CORPUS_timedata.tsv.gz instead of the MySQL database
t|test
    test whether the .info files need updating
u|update
    update the .info files for the corpora if needed
v|verbose
    show information about the processed corpora
A|all all_corpora
    process all corpora in the CWB corpus registry
no-backups !backups
    do not make backups of the info files when updating
backup-suffix=SUFFIX ".bak"
    use SUFFIX as the backup file suffix
'

. $progdir/korp-lib.sh


std_info_keys_list="Sentences Updated FirstDate LastDate"
std_info_keys=$(echo "$std_info_keys_list" | sed -e 's/ /|/g')

if which wdiff > /dev/null 2>&1; then
    wdiff=wdiff
else
    wdiff=diff
fi


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
eval "$optinfo_opt_handler"


cwb_describe_corpus=$(find_prog cwb-describe-corpus $cwb_bindir)
cwb_s_decode=$(find_prog cwb-s-decode $cwb_bindir)

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

get_date_mysql () {
    _type=$1
    _corpname=$2
    _corpname_u=$(echo "$_corpname" | sed -e 's/.*/\U&\E/')
    if [ "x$_type" = "xfirst" ]; then
	_func=min
	_field=datefrom
    else
	_func=max
	_field=dateto
    fi
    run_mysql "select $_func($_field) from timedata where corpus='$_corpname_u' and $_field != '0000-00-00 00:00:00';" |
    tail -1 |
    grep -v '^NULL$'
}

get_date_tsv () {
    local type corpname fieldnr sort_opts
    type=$1
    corpname=$2
    if [ "x$type" = "xfirst" ]; then
	fieldnr=2
	sort_opts=-n
    else
	fieldnr=3
	sort_opts=-nr
    fi
    comprcat $tsvdir/${corpus}_timedata.tsv* |
    cut -d"$tab" -f$fieldnr |
    grep -v '^0*$' |
    sort $sort_opts |
    head -1 |
    sed -e 's/\([0-9][0-9][0-9][0-9]\)\([0-9][0-9]\)\([0-9][0-9]\)\([0-9][0-9]\)\([0-9][0-9]\)\([0-9][0-9]\)/\1-\2-\3 \4:\5:\6/'
}

get_date () {
    corpname=$2
    if [ "x$tsvdir" != x ]; then
	 if test_compr_file -s "$tsvdir/${corpname}_timedata.tsv"; then
	     get_date_tsv "$@"
	 else
	     # FIXME: The message is inexact, as test_compr_file and
	     # comprcat also recognize .bz2 and .xz files.
	     warn "File $tsvdir/${corpname}_timedata.tsv(.gz) not found or empty: cannot get FirstDate and LastDate information"
	 fi
    elif [ "x$mysql_bin" != x ]; then
	get_date_mysql "$@"
    else
	warn "No MySQL client found and no --tsv-dir specified: cannot get FirstDate and LastDate information"
    fi
}

extract_info () {
    corpdir=$1
    corpname=$2
    sentcount=$(get_sentence_count $corpname)
    updated=$(get_updated "$corpdir")
    firstdate=$(get_date first $corpname)
    lastdate=$(get_date last $corpname)
    echo "Sentences: $sentcount"
    echo "Updated: $updated"
    if [ "x$firstdate" != x ]; then
	echo "FirstDate: $firstdate"
    fi
    if [ "x$lastdate" != x ]; then
	echo "LastDate: $lastdate"
    fi
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
    corpora=$(list_corpora "*")
else
    corpora=$(list_corpora $*)
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
	ensure_perms $outfile $outfile$backup_suffix
    fi
done
