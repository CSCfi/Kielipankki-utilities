#! /bin/bash
# -*- coding: utf-8 -*-


# TODO:
# - Check that the existing corpus does not already have the
#   attributes to be added.
# - Optionally re-encode the corpus completely, including existing
#   positional and structural attributes.


progname=`basename $0`
progdir=`dirname $0`

shortopts="hc:"
longopts="help,corpus-root:,input-attrs:,input-fields:,lemgram-posmap:,posmap:,wordpict-relmap:,wordpicture-relation-map:,relmap:,tsv-dir:,import-database,verbose"

. $progdir/korp-lib.sh

vrt_fix_attrs=$progdir/vrt-fix-attrs.py
vrt_add_lemgrams=$progdir/vrt-add-lemgrams.py
vrt_convert_chars=$progdir/vrt-convert-chars.py
vrt_extract_lemgrams=$progdir/vrt-extract-lemgrams.sh
run_extract_rels=$progdir/run-extract-rels.sh
korp_mysql_import=$progdir/korp-mysql-import.sh

cwb_encode=$cwb_bindir/cwb-encode
cwb_describe_corpus=$cwb_bindir/cwb-describe-corpus
# cwb-make is in the CWB/Perl package, so it might be in a different directory
cwb_make=$(find_prog cwb-make $default_cwb_bindirs)

mapdir=$progdir/../corp

tsv_subdir=vrt/CORPUS

initial_input_attrs="ref lemma pos msd dephead deprel"
lemgram_posmap=$mapdir/lemgram_posmap_tdt.tsv
wordpict_relmap=$mapdir/wordpict_relmap_tdt.tsv
name_tags=
import_database=
tsvdir=
verbose=


usage () {
    cat <<EOF
Usage: $progname [options] corpus [input_file ...]

Add dependency parses and information derived from them to an existing Korp
corpus.

The input files may be either (possibly compressed) VRT files containing
dependency parse information and name tags, or ZIP or (possibly compressed)
tar archives containing such VRT files. If no input files are specified, read
from the standard input.

Options:
  -h, --help      show this help
  -c, --corpus-root DIR
                  use DIR as the root directory of corpus files (default:
                  $corpus_root)
  --input-attrs ATTRS
                  specify the names of the positional attributes in the input,
                  excluding the first one ("word" or token), separated by
                  spaces (default: "$initial_input_attrs")
  --lemgram-posmap POSMAP_FILE
                  use POSMAP_FILE as the mapping file from the corpus parts of
                  speech to those used in Korp lemgrams; the file should
                  contain lines with corpus POS and lemgram POS separated by
                  a tab (default: $lemgram_posmap)
  --wordpict-relmap RELMAP_FILE
                  use RELMAP_FILE as the mapping file from corpus dependency
                  relations to those used in the Korp word picture; the file
                  should contain lines with corpus POS and lemgram POS
                  separated by a tab (default: $wordpict_relmap)
  --tsv-dir DIR   output database tables as TSV files to DIR (default:
                  $corpus_root/$tsv_subdir)
  --import-database
                  import the database TSV files into the Korp MySQL database
  --verbose       output some progress information
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
	--input-attrs | --input-fields )
	    shift
	    initial_input_attrs=$1
	    ;;
	--lemgram-posmap | --posmap )
	    shift
	    lemgram_posmap=$1
	    ;;
	--wordpict-relmap | --relmap | --wordpicture-relation-map )
	    shift
	    wordpict_relmap=$1
	    ;;
	--tsv-dir )
	    shift
	    tsvdir=$1
	    ;;
	# --name-tags )
	#     name_tags=1
	#     ;;
	--import-database )
	    import_database=1
	    ;;
	--verbose )
	    verbose=1
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


if [ "x$1" = "x" ]; then
    error "No corpus name specified"
fi
corpus=$1
shift

if [ ! -e $corpus_root/registry/$corpus ]; then
    error "Corpus $corpus does not exist"
fi

tsvdir=${tsvdir:-$corpus_root/$tsv_subdir}
tsvdir=${tsvdir//CORPUS/$corpus}

mkdir -p $tsvdir

if [ "x$name_tags" != x ]; then
    initial_input_attrs="$initial_input_attrs nertag"
fi

input_attrs=$(
    echo "$initial_input_attrs lex" |
    sed -e 's/lemma/& lemmacomp/'
)

vrt_file=$tmp_prefix.vrt


cat_input () {
    if [ "x$1" = x ]; then
	cat
    else
	for fname in "$@"; do
	    if [ ! -r "$fname" ]; then
		error "Unable to read input file: $fname"
	    fi
	    case $fname in
		*.tgz | *.tar.gz )
		    tar xzOf "$fname"
		    ;;
		*.tbz | *.tbz2 | *.tar.bz2 )
		    tar xjOf "$fname"
		    ;;
		*.txz | *.tar.xz )
		    tar xJOf "$fname"
		    ;;
		*.tar )
		    tar xOf "$fname"
		    ;;
		*.gz )
		    zcat "$fname"
		    ;;
		*.bz2 )
		    bzcat "$fname"
		    ;;
		*.xz )
		    xzcat "$fname"
		    ;;
		*.zip )
		    unzip -p "$fname"
		    ;;
		* )
		    cat "$fname"
		    ;;
	    esac
	done
    fi
}


add_lemmas_without_boundaries () {
    $vrt_fix_attrs --input-fields "word $initial_input_attrs" \
	--output-fields "word $(echo "$initial_input_attrs" | sed -e 's/lemma/lemma:noboundaries lemma/')" \
	--compound-boundary-marker='|' --compound-boundary-can-replace-hyphen
}

add_lemgrams () {
    $vrt_add_lemgrams --pos-map-file "$lemgram_posmap" \
	--lemma-field=3 --pos-field=5
}

check_corpus_size () {
    curr_size=$(
	$cwb_describe_corpus $corpus |
	grep -E '^size \(tokens\)' |
	awk '{print $NF}'
    )
    new_size=$(grep -E -cv '^<' $vrt_file)
    if [ $curr_size != $new_size ]; then
	error "The input has $new_size tokens, whereas the existing corpus has $curr_size; aborting"
    fi
}

run_cwb_encode () {
    # TODO: Split encoding lemgrams separately, so that it should be
    # faster to encode the special character, without having to take
    # into account the lemgram feature set attribute.
    posattrcount=$(echo "$input_attrs" | wc -w)
    egrep -v '^<' $vrt_file |
    cut -d'	' -f2- |
    $vrt_convert_chars --feature-set-attributes $posattrcount |
    $cwb_encode -d $corpus_root/data/$corpus -p - -xsB -c utf8 \
	$(add_prefix "-P " $input_attrs)
}

add_registry_attrs () {
    regfile=$corpus_root/registry/$corpus
    cp -p $regfile $regfile.bak
    # Add the new attributes after word
    sed -e '/^ATTRIBUTE word/ a'"$(add_prefix '\
ATTRIBUTE ' $input_attrs)" $regfile.bak > $regfile
}

run_cwb_make () {
    $cwb_make -V $corpus
}

extract_lemgrams () {
    $vrt_extract_lemgrams --corpus-id $corpus < $vrt_file |
    gzip > $tsvdir/${corpus}_lemgrams.tsv.gz
}

extract_wordpict_rels () {
    $run_extract_rels --corpus-name $corpus \
	--input-fields "word $input_attrs" \
	--output-dir "$tsvdir" --relation-map "$wordpict_relmap" \
	--optimize-memory --no-tar \
	< $vrt_file
}

import_database () {
    $korp_mysql_import --prepare-tables --relations-format new \
	$tsv_dir/${corpus}_lemgrams.tsv.gz $tsv_dir/${corpus}_rels*.tsv.gz
}

main () {
    echo_verb "Adding parse information to Korp corpus $corpus:"
    echo_verb "Adding lemgrams and lemmas without compound boundaries"
    set -o pipefail
    cat_input "$@" |
    add_lemmas_without_boundaries |
    add_lemgrams > $vrt_file
    if [ $? != 0 ]; then
	exit_on_error false
    fi
    check_corpus_size
    echo_verb "Encoding the the new attributes"
    exit_on_error run_cwb_encode
    exit_on_error add_registry_attrs
    echo_verb "Indexing and compressing the new attributes"
    exit_on_error run_cwb_make
    echo_verb "Extracting lemgrams for the database"
    exit_on_error extract_lemgrams
    echo_verb "Extracting word picture relations for the database"
    exit_on_error extract_wordpict_rels
    if [ "x$import_database" != x ]; then
	echo_verb "Importing data to the MySQL database"
	exit_on_error import_database
    fi
    echo_verb "Completed."
}

main "$@"
