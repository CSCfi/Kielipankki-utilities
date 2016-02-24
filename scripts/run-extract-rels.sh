#! /bin/bash

progname=`basename $0`
progdir=`dirname $0`
cmdline="$@"

export LC_ALL=C

shortopts="hc:f:r:o:v"
longopts="help,corpus-name:,input-fields:,relation-map:,output-dir:,optimize-memory,no-tar,no-archive,keep-temp-files,verbose"

corpus_name=
input_fields=
relation_map=
input=
output_dir=.
optimize_memory=
keep_temp_files=
verbose=
make_archive=1

extract_rels_opts="--output-type=new-strings --word-form-pair-type=baseform"

. $progdir/korp-lib.sh

usage () {
    cat <<EOF
Usage: $progname [options]

Extract dependency relations from VRT files to TSV files for the Korp
word picture.

This is a wrapper script for vrt-extract-relations.py. This script
sorts the output tables outside the Python script, produces a tar
archive of the relations files and optionally writes log output.

Options:
  -h, --help
  -c, --corpus-name CORPUS
  -f, --input-fields FIELDLIST
  -r, --relation-map FILE
  -i, --input FILESPEC
  -o, --output-dir DIR
  --optimize-memory
  --no-tar, --no-archive
  --keep-temp-files
  -v, --verbose
EOF
    exit 0
}

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	-c | --corpus-name )
	    corpus_name=$2
	    shift
	    ;;
	-f | --input-fields )
	    input_fields=$2
	    shift
	    ;;
	-r | --relation-map )
	    relation_map=$2
	    shift
	    ;;
	-i | --input )
	    # FIXME: This is unimplemented; what was the original idea?
	    input=$2
	    shift
	    ;;
	-o | --output-dir )
	    output_dir=$2
	    shift
	    ;;
	--optimize-memory )
	    optimize_memory=1
	    extract_rels_opts="$extract_rels_opts --raw-output"
	    ;;
	--keep-temp-files )
	    keep_temp_files=1
	    cleanup_on_exit=
	    ;;
	--no-tar | --no-archive )
	    make_archive=
	    ;;
	-v | --verbose )
	    verbose=1
	    ;;
	-- )
	    shift
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

if [ "x$corpus_name" = "x" ]; then
    error "Please specify corpus name with --corpus-name"
fi
if [ "x$input_fields" = x ]; then
    error "Please specify input field names with --input-fields"
fi
if [ "x$relation_map" = x ]; then
    error "Please specify relation map file with --relation-map"
fi

tempdir_usage () {
    printf "Tempdir usage: "
    du -sh $tmpfile_dir |
    cut -d'	' -f1
}

sort_and_gzip () {
    for f in "$@"; do
	mv $f $f.unsorted
	sort_opts=
	case $f in
	    *_rels.tsv | *_rels_sentences.tsv | *_rels_strings.tsv )
		sort_opts=-n
		;;
	esac
	sort $sort_opts $f.unsorted | gzip > $f.gz
    done
}

process_raw_output () {
    # Tab, to be used in sed expressions for better compatibility
    # than \t
    tab='	'
    base_name=$tmpfile_dir/${corpus_name}_rels
    for reltype in head_rel dep_rel; do
	sort -n ${base_name}_${reltype}.raw.tsv |
	uniq -c |
	sed -e "s/^ *\([0-9]\+\) \(.*\)/\2${tab}\1/" |
	gzip > ${base_name}_${reltype}.tsv.gz
    done
    fifo=$tmpfile_dir/rel_ids.fifo
    rel_ids_fname=$tmpfile_dir/rel_ids.tsv
    mkfifo $fifo
    (
	sort -nr |
	sed -e "s/^ *\([0-9]\+\)${tab} *[0-9]\+ \([^ ${tab}]\+\).*/\2${tab}\1/" < $fifo |
	sort -t"${tab}" -k1,1 > $rel_ids_fname
    ) &
    fifo_pid=$!
    sort ${base_name}.raw.tsv |
    uniq -c |
    cat -n |
    tee $fifo |
    sed -e "s/^ *\([0-9]\+\)${tab} *\([0-9]\+\) \([^${tab}]\+\)${tab}\([^${tab}]\+${tab}[^${tab}]\+${tab}[^${tab}]\+\)/\1${tab}\4${tab}\2/" |
    gzip > ${base_name}.tsv.gz
    wait $fifo_pid
    sort -t"${tab}" -k1,1 ${base_name}_sentences.raw.tsv |
    join -t"${tab}" -j1 -o '2.2 1.2 1.3 1.4' - $rel_ids_fname |
    sort -n |
    gzip > ${base_name}_sentences.tsv.gz
    sort_and_gzip ${base_name}_rel.tsv ${base_name}_strings.tsv
}

hostenv=`get_host_env`

verbose echo Run: $0 "$cmdline"
verbose echo Corpus: $corpus_name
verbose echo_timestamp Start

rels_tar=${corpus_name}_rels.tar
tmpfile_dir=$tmp_prefix.work

if [ "x$make_archive" = x ] || [ ! -e $output_dir/$rels_tar ]; then
    if [ "x$hostenv" = "xtaito" ]; then
	module load python-env/2.7.6
    fi
    mkdir -p $output_dir $tmpfile_dir
    verbose echo_timestamp vrt-extract-relations
    $progdir/vrt-extract-relations.py \
	--output-prefix "$tmpfile_dir/${corpus_name}_rels" \
	--input-fields "$input_fields" \
	--relation-map "$relation_map" \
	$extract_rels_opts
    verbose subproc_times
    # --sort --compress=gzip --temporary-files
    # Sorting and compressing files within vrt-extract-relations.py
    # often seems to leave the rels_sentences file incomplete. Why?
    verbose tempdir_usage
    if [ "x$optimize_memory" != x ]; then
	verbose echo_timestamp Postprocess: raw output
	process_raw_output
    else
	verbose echo_timestamp Postprocess: sort and gzip
	sort_and_gzip $tmpfile_dir/*.tsv
    fi
    verbose subproc_times
    verbose tempdir_usage
    verbose echo_timestamp tar
    real_output_dir=$output_dir
    output_dir_firstchar=${output_dir:0:1}
    if [ "x$output_dir_firstchar" != x/ ] &&
	[ "x$output_dir_firstchar" != x~ ]
    then
	real_output_dir=$(pwd)/$output_dir
    fi
    # tar cpf $rels_tar -C $output_dir --wildcards \*_rels\*.gz
    # Wildcards do not seem to work above in tar even with --wildcards. Why?
    (
	cd $tmpfile_dir
	if [ "x$make_archive" != x ]; then
	    tar cpf $real_output_dir/$rels_tar --wildcards \
		${corpus_name}_rels*.tsv.gz
	else
	    mv ${corpus_name}_rels*.tsv.gz $real_output_dir
	fi
    )
    verbose subproc_times
    if [ "x$keep_temp_files" = x ]; then
	rm -rf $tmpfile_dir
    fi
fi

verbose echo_timestamp End
