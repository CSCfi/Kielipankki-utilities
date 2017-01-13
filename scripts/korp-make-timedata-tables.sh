#! /bin/sh
# -*- coding: utf-8 -*-

# Usage: korp-make-timedata-tables.sh [options] corpus ...
#
# For more information, run korp-make-timedata-tables.sh --help


progname=`basename $0`
progdir=`dirname $0`

shortopts="hc:t:v"
longopts="help,corpus-root:,tsv-dir:,verbose,import"

tsvdir=$CORPUS_TSVDIR
tsvsubdir=sql
verbose=
import=

dbname="korp"

. $progdir/korp-lib.sh


usage () {
    cat <<EOF
Usage: $progname [options] corpus ...

Generate Korp timedata database tables based on text attributes datefrom,
dateto, timefrom and timeto, and import them into the Korp MySQL database.

Corpus names are specified in lower case. Shell wildcards may be used in them.

Options:
  -h, --help      show this help
  -c, --corpus-root DIR
                  use DIR as the root directory of corpus files for the
                  source files (CORPUS_ROOT) (default: $corpus_root)
  -t, --tsv-dir DIRTEMPL
                  use DIRTEMPL as the directory template to which to write
                  Korp MySQL TSV data files; DIRTEMPL is a directory name
                  possibly containing the placeholder {corpid} for corpus id
                  (default: CORPUS_ROOT/$tsvsubdir)
  --import-database
                  import data into the Korp MySQL database
  -v, --verbose   verbose output
EOF
    exit 0
}

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	-c | --corpus-root )
	    shift
	    set_corpus_root "$1"
	    ;;
	-t | --tsv-dir )
	    shift
	    tsvdir=$1
	    ;;
	-v | --verbose )
	    verbose=1
	    ;;
	--import-database )
	    import=1
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


tsvdir=${tsvdir:-$corpus_root/$tsvsubdir}

corpora=$(list_corpora "$@")

verbose_opt=
if [ "x$verbose" != x ]; then
    verbose_opt=--verbose
fi

descr_corpus="$cwb_bindir/cwb-describe-corpus"
s_decode="$cwb_bindir/cwb-s-decode"
mysql_import="/v/korp/scripts/korp-mysql-import.sh --prepare-tables"


generate_timedata () {
    # TODO: This is largely copied from korp-convert-timedata.sh; how
    # to have the code in one place only?
    _corpus=$1
    _corpus_u=$(echo $_corpus | sed -e 's/.*/\U&\E/')
    tsvdir_real=$(echo "$tsvdir" | sed -e "s/{corpid}/$_corpus/g")
    if ! mkdir -p $tsvdir_real 2> /dev/null; then
	error "Cannot create TSV directory $tsvdir_real"
    fi
    timedata_tsv=$tsvdir_real/${_corpus}_timedata.tsv.gz
    timedata_date_tsv=$tsvdir_real/${_corpus}_timedata_date.tsv.gz
    $s_decode $_corpus -S text > $tmp_prefix.text.tsv 2> $tmp_prefix.text.err
    if grep -q "Can't access s-attribute" $tmp_prefix.text.err; then
	echo_verb "    No structural attribute 'text' in corpus $_corpus; skipping"
	return
    fi
    for attrname in datefrom timefrom dateto timeto; do
	_fname=$tmp_prefix.$attrname.tsv
	$s_decode $_corpus -S text_$attrname 2> $_fname.err |
	cut -d"$tab" -f3 > $_fname
	if grep -q "Can't access s-attribute" $_fname.err; then
	    cat /dev/null > $_fname
	fi
    done
    for fromto in from to; do
	paste $tmp_prefix.date$fromto.tsv $tmp_prefix.time$fromto.tsv |
	tr -d '\t' > $tmp_prefix.$fromto.tsv
    done
    paste $tmp_prefix.text.tsv $tmp_prefix.from.tsv $tmp_prefix.to.tsv |
    gawk -F"$tab" '{print "'"$_corpus_u"'\t" $3 "\t" $4 "\t" $2 - $1 + 1}' |
    $progdir/timespans-adjust-granularity.py \
	--granularity=second --from-field=2 --to-field=3 --count-field=4 |
    sort | gzip > $timedata_tsv
    zcat $timedata_tsv |
    $progdir/timespans-adjust-granularity.py \
	--granularity=day --from-field=2 --to-field=3 --count-field=4 |
    sort | gzip > $timedata_date_tsv
    tokencnt=$($descr_corpus $_corpus | gawk '/^size / {print $NF}')
    for file in $timedata_tsv $timedata_date_tsv; do
        timedata_tokencnt=$(
            zcat $file |
	    gawk -F"$tab" '{s+=$4} END {print s}'
	)
        if [ "x$timedata_tokencnt" != "x$tokencnt" ]; then
            echo "Error: Corpus has $tokencnt tokens but database table in $file $timedata_tokencnt tokens"
            exit 1
        fi
    done
    if [ "x$import" != x ]; then
	echo_verb "  Importing data into the Korp MySQL database"
	$progdir/korp-mysql-import.sh --prepare-tables \
	    $timedata_tsv $timedata_date_tsv |
	cat_verb |
	indent_input 4
    fi
}


for corpus in $corpora; do
    echo_verb "Generating time data for corpus $corpus"
    generate_timedata $corpus
done
