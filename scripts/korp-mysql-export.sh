#! /bin/sh


# Usage: korp-mysql-export.sh [options] corpus_id ...
#
# For more information, run korp-mysql-export.sh --help


progname=`basename $0`
progdir=`dirname $0`

usage_header="Usage: $progname [options] corpus_id ...

Export data from Korp MySQL database tables into TSV files for corpora with
ids corpus_id ... corpus_id may contain shell wildcards, in which case all
matching corpora in the corpus registry are processed."

optspecs='
c|corpus-root=DIR "$corpus_root" { set_corpus_root "$1" }
    use DIR as the root directory of corpus files for the source files
    (CORPUS_ROOT) (default: $corpus_root)
o|output-dir=DIRTEMPL "CORPUS_ROOT/$tsvsubdir" outputdir
    use DIRTEMPL as the output directory template for TSV files;
    DIRTEMPL is a directory name possibly containing placeholder
    {corpid} for corpus id
q|quiet { verbose= }
    suppress all output
v|verbose { verbose=2 }
    verbose output: show the TSV files produced and the number of rows
    in them
z|compress=PROG "$compress" { set_compress "$1" }
    compress files with PROG; "none" for no compression
'

usage_footer="Environment variables:
  Default values for the various directories can also be specified via
  the following environment variables: CORPUS_ROOT, CORPUS_REGISTRY,
  CORPUS_TSVDIR."


. $progdir/korp-lib.sh


tsvsubdir=vrt/{corpid}
compress=gzip
outputdir=
verbose=1

dbname=korp

tables_common="lemgram_index timedata timedata_date auth_license auth_lbr_map"
tables_by_corpus="relations"
table_suffixes_relations="@ dep_rel head_rel rel sentences strings"
filename_lemgram_index=lemgrams
filename_corpus_info=corpinfo
filename_relations=rels

compr_suffix_gzip=.gz
compr_suffix_bzip2=.bz2
compr_suffix_xz=.xz
compr_suffix_cat=


# Set $compress to $1, "cat" if "none"; warn if program $1 not found.
set_compress () {
    if [ "x$1" = "xnone" ]; then
	compress=cat
    elif which $1 > /dev/null; then
	compress=$1
    else
	warn "Compression program $1 not found; using $compress"
    fi
}


# Process options
eval "$optinfo_opt_handler"


if [ "x$1" = x ]; then
    error "Please specify the names (ids) of corpora whose data to export.
For more information, run '$0 --help'."
fi

outputdir=${outputdir:-$corpus_root/$tsvsubdir}

corpora=$(list_corpora "$@")

fname_suffix=.tsv$(eval echo \$compr_suffix_$compress)

if [ "x$MYSQL_USER" != "x" ]; then
    mysql_opt_user="--user $MYSQL_USER"
fi


run_mysql_export () {
    local tablename outfname sql_cmd pid rowcnt
    tablename=$1
    outfname=$2
    sql_cmd=$3
    shift 3
    # SET SQL_BIG_SELECTS=1 is needed for exporting large tables
    sql_cmd="SET SQL_BIG_SELECTS=1; $sql_cmd"
    if [ ! -e $tmp_prefix.fifo ]; then
	mkfifo $tmp_prefix.fifo
    fi
    wc -l < $tmp_prefix.fifo > $tmp_prefix.wc &
    pid=$!
    run_mysql --table $tablename "$sql_cmd" "$@" 2> $tmp_prefix.err |
    tail -n+2 |
    tee $tmp_prefix.fifo |
    $compress > $outfname
    wait $pid
    rowcnt=$(cat $tmp_prefix.wc)
    if [ $rowcnt = 0 ]; then
	if [ -s $tmp_prefix.err ] &&
	       # Silently ignore "Table doesn't exist" errors
	       ! grep -lq '^ERROR 1146' $tmp_prefix.err;
	then
	    warn "Table $tablename not exported due to a MySQL error:"
	    cat $tmp_prefix.err | sed -e 's/^/  /'
	fi
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
