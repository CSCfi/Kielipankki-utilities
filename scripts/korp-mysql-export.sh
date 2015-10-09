#! /bin/sh


# Usage: korp-mysql-export.sh [options] corpus_id ...
#
# For more information, run korp-mysql-export.sh --help


progname=`basename $0`
progdir=`dirname $0`

shortopts="hc:o:qvz:"
longopts="help,corpus-root:,output-dir:,quiet,verbose,compress:"

. $progdir/korp-lib.sh

tsvsubdir=vrt/{corpid}
compress=gzip
outputdir=
verbose=1

dbname=korp

tables_common="lemgram_index timespans corpus_info"
tables_by_corpus="relations names"
table_suffixes_relations="@ dep_rel head_rel rel sentences strings"
table_suffixes_names="@ sentences strings"
filename_lemgram_index=lemgrams
filename_corpus_info=corpinfo
filename_relations=rels

compr_suffix_gzip=.gz
compr_suffix_bzip2=.bz2
compr_suffix_xz=.xz
compr_suffix_cat=


usage () {
    cat <<EOF
Usage: $progname [options] corpus_id ...

Export data from Korp MySQL database tables into TSV files for corpora with
ids corpus_id ... corpus_id may contain shell wildcards, in which case all
matching corpora in the corpus registry are processed.

Options:
  -h, --help      show this help
  -c, --corpus-root DIR
                  use DIR as the root directory of corpus files for the
                  source files (CORPUS_ROOT) (default: $corpus_root)
  -o, --output-dir DIRTEMPL
                  use DIRTEMPL as the output directory template for TSV files;
                  DIRTEMPL is a directory name possibly containing placeholder
                  {corpid} for corpus id (default: CORPUS_ROOT/$tsvsubdir)
  -q, --quiet     suppress all output
  -v, --verbose   verbose output: show the TSV files produced and the number
                  of rows in them
  -z, --compress PROG
                  compress files with PROG; "none" for no compression
                  (default: $compress)

Environment variables:
  Default values for the various directories can also be specified via
  the following environment variables: CORPUS_ROOT, CORPUS_REGISTRY,
  CORPUS_TSVDIR.
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
	    corpus_root=$1
	    ;;
	-o | --output-dir )
	    shift
	    outputdir=$1
	    ;;
	-q | --quiet )
	    verbose=
	    ;;
	-v | --verbose )
	    verbose=2
	    ;;
	-z | --compress )
	    shift
	    if [ "x$1" = "xnone" ]; then
		compress=cat
	    elif which $1 > /dev/null; then
		compress=$1
	    else
		warn "Compression program $1 not found; using $compress"
	    fi
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

if [ "x$1" = x ]; then
    error "Please specify the names (ids) of corpora whose data to export.
For more information, run '$0 --help'."
fi

outputdir=${outputdir:-$corpus_root/$tsvsubdir}
regdir=${CORPUS_REGISTRY:-$corpus_root/registry}

corpora=$(list_corpora $regdir "$@")

fname_suffix=.tsv$(eval echo \$compr_suffix_$compress)

if [ "x$MYSQL_USER" != "x" ]; then
    mysql_opt_user="--user $MYSQL_USER"
fi


run_mysql () {
    mysql $mysql_opt_user --batch --raw --execute "$@" $dbname
}

run_mysql_export () {
    tablename=$1
    outfname=$2
    shift
    shift
    if [ ! -e $tmp_prefix.fifo ]; then
	mkfifo $tmp_prefix.fifo
    fi
    wc -l < $tmp_prefix.fifo > $tmp_prefix.wc &
    pid=$!
    run_mysql "$@" 2> /dev/null |
    tail -n+2 |
    tee $tmp_prefix.fifo |
    $compress > $outfname
    wait $pid
    rowcnt=$(cat $tmp_prefix.wc)
    if [ $rowcnt = 0 ]; then
	rm $outfname
    else
	verbose 2 echo "  $tablename ($rowcnt rows): $outfname"
    fi
    if [ -s $tmp_prefix.tsv ]; then
	$compress < $tmp_prefix.tsv > $outfname
    fi
}

export_common_table () {
    corpid=$1
    corpid_u=$2
    outdir=$3
    table=$4
    fname_table=$(eval echo \$filename_$table)
    outfname=${corpid}_${fname_table:-$table}$fname_suffix
    run_mysql_export $table $outdir/$outfname \
	"SELECT * FROM $table WHERE corpus='$corpid_u';"
}

export_by_corpus_tables () {
    corpid=$1
    corpid_u=$2
    outdir=$3
    tablegroup=$4
    for table_suff in $(eval echo \$table_suffixes_$tablegroup); do
	if [ $table_suff = @ ]; then
	    table_suff=
	else
	    table_suff=_$table_suff
	fi
	table=${tablegroup}_$corpid_u$table_suff
	fname_table=$(eval echo \$filename_$tablegroup)
	outfname=${corpid}_${fname_table:-$tablegroup}$table_suff$fname_suffix
	run_mysql_export $table $outdir/$outfname "SELECT * FROM $table;"
    done
}

mysql_export () {
    corpid=$1
    verbose 1 echo "Corpus $corpid"
    outputdir_real=$(echo "$outputdir" | sed -e "s/{corpid}/$corpid/g")
    mkdir -p $outputdir_real
    corpid_u=$(echo "$corpid" | sed -e 's/.*/\U&\E/')
    for table in $tables_common; do
	export_common_table $corpid $corpid_u $outputdir_real $table
    done
    for tablegroup in $tables_by_corpus; do
	export_by_corpus_tables $corpid $corpid_u $outputdir_real $tablegroup
    done
}


verbose 1 echo "Exporting Korp MySQL database tables"
for corpus in $corpora; do
    mysql_export $corpus
done
