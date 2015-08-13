#! /bin/bash

progname=`basename $0`
progdir=`dirname $0`

shortopts="hc:f:r:o:"
longopts="help,corpus-name:,input-fields:,relation-map:,output-dir:,keep-temp-files"

corpus_name=
input_fields=
relation_map=
input=
output_dir=.
keep_temp_files=

extract_rels_opts="--output-type=new-strings --word-form-pair-type=baseform"

. $progdir/korp-lib.sh

usage () {
    cat <<EOF
Usage: $progname [options]

Extract dependency relations from VRT files to TSV files for the Korp
word picture.

This is a wrapper script for vrt-extract-relations.py. This script
sorts the output tables outside the Python script, produces a tar
archive of the relations files and writes log output.

Options:
  -h, --help
  -c, --corpus-name CORPUS
  -f, --input-fields FIELDLIST
  -r, --relation-map FILE
  -i, --input FILESPEC
  -o, --output-dir DIR
  --keep-temp-files
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
	    input=$2
	    shift
	    ;;
	-o | --output-dir )
	    output_dir=$2
	    shift
	    ;;
	--keep-temp-files )
	    keep_temp_files=1
	    cleanup_on_exit=
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

hostenv=`get_host_env`

date +'Start: %F %T %s.%N'

echo Corpus: $corpus_name
rels_tar=${corpus_name}_rels.tar
tmpfile_dir=$tmp_prefix.work

if [ ! -e $rels_tar ]; then
    if [ "x$hostenv" = "xtaito" ]; then
	module load python-env/2.7.6
    fi
    mkdir -p $output_dir $tmpfile_dir

    $progdir/vrt-extract-relations.py \
	--output-prefix "$tmpfile_dir/${corpus_name}_rels" \
	--input-fields "$input_fields" \
	--relation-map "$relation_map" \
	$extract_rels_opts
    # --sort --compress=gzip --temporary-files
    # Sorting and compressing files within vrt-extract-relations.py
    # often seems to leave the rels_sentences file incomplete. Why?
    for f in $tmpfile_dir/*.tsv; do
	mv $f $f.unsorted
	sort_opts=
	case $f in
	    *_rels.tsv | *_rels_sentences.tsv | *_rels_strings.tsv )
		sort_opts=-n
		;;
	esac
	sort $sort_opts $f.unsorted | gzip > $f.gz
    done
    # tar cpf $rels_tar -C $output_dir --wildcards \*_rels\*.gz
    # Wildcards do not seem to work above in tar even with --wildcards. Why?
    (
	cd $tmpfile_dir
	tar cpf $output_dir/$rels_tar --wildcards ${corpus_name}_rels*.tsv.gz
    )
    if [ "x$keep_temp_files" = x ]; then
	rm -rf $tmpfile_dir
    fi
fi

date +'End: %F %T %s.%N'
