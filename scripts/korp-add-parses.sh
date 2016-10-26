#! /bin/bash
# -*- coding: utf-8 -*-


# TODO:
# - Optionally re-encode the corpus completely, including existing
#   positional and structural attributes.
# - Allow different compound boundary options.


progname=`basename $0`
progdir=`dirname $0`

shortopts="hc:"
longopts="help,corpus-root:,input-attrs:,input-fields:,name-tags,ner-tags,name-attributes,name-attrs,save-augmented-vrt-file:,augmented-vrt-input,lemgram-posmap:,posmap:,wordpict-relmap:,wordpicture-relation-map:,relmap:,tsv-dir:,no-wordpicture,skip-wordpicture,import-database,verbose,times"

. $progdir/korp-lib.sh

# cleanup_on_exit=

vrt_fix_attrs=$progdir/vrt-fix-attrs.py
vrt_add_lemgrams=$progdir/vrt-add-lemgrams.py
vrt_convert_chars=$progdir/vrt-convert-chars.py
vrt_extract_lemgrams=$progdir/vrt-extract-lemgrams.sh
run_extract_rels=$progdir/run-extract-rels.sh
vrt_add_name_attrs=$progdir/vrt-add-name-attrs.sh
korp_mysql_import=$progdir/korp-mysql-import.sh

cwb_encode=$cwb_bindir/cwb-encode
cwb_describe_corpus=$cwb_bindir/cwb-describe-corpus
# cwb-make is in the CWB/Perl package, so it might be in a different directory
cwb_make=$(find_prog cwb-make $default_cwb_bindirs)

mapdir=$progdir/../corp

tsv_subdir=vrt/CORPUS

initial_input_attrs="ref lemma pos msd dephead deprel"
vrt_file=$tmp_prefix.vrt
augmented_vrt_input=
lemgram_posmap=$mapdir/lemgram_posmap_tdt.tsv
wordpict_relmap=$mapdir/wordpict_relmap_tdt.tsv
name_attrs=
import_database=
wordpicture=1
tsvdir=
verbose=
show_times=


usage () {
    cat <<EOF
Usage: $progname [options] corpus [input_file ...]

Add dependency parses and information derived from them to an existing Korp
corpus. Optionally also add named-entity information.

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
  --name-attrs    add named-entity information based on a NER tag as the last
                  positional attribute
  --save-augmented-vrt-file VRT_FILE
                  save as VRT_FILE the VRT file with the added attributes
                  (lemmas without compound boundaries and lemgrams); the file
                  can be used as input with --augmented-vrt-input, e.g., to
                  resume faster an interrupted run
  --augmented-vrt-input
                  the input VRT contains the added attributes
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
  --no-wordpicture
                  do not extract word picture relations database tables
  --import-database
                  import the database TSV files into the Korp MySQL database
  --verbose       output some progress information
  --times         output the amount of CPU time used for each stage
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
	--input-attrs | --input-fields )
	    shift
	    initial_input_attrs=$1
	    ;;
	--save-augmented-vrt-file )
	    shift
	    vrt_file=$1
	    ;;
	--augmented-vrt-input )
	    augmented_vrt_input=1
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
	--name-tags | --ner-tags | --name-attributes | --name-attrs )
	    name_attrs=1
	    ;;
	--no-wordpicture | --skip-wordpicture )
	    wordpicture=
	    ;;
	--import-database )
	    import_database=1
	    ;;
	--verbose )
	    verbose=1
	    ;;
	--times )
	    show_times=1
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

if [ ! -e $cwb_regdir/$corpus ]; then
    error "Corpus $corpus does not exist"
fi

input_files=( "$@" )

tsvdir=${tsvdir:-$corpus_root/$tsv_subdir}
tsvdir=${tsvdir//CORPUS/$corpus}

mkdir -p $tsvdir

if [ "x$name_attrs" != x ]; then
    initial_input_attrs="$initial_input_attrs nertag"
fi

if [ "x$augmented_vrt_input" != x ]; then
    if [[ "$initial_input_attrs" != "* lemmacomp *" ]]; then
	initial_input_attrs=${initial_input_attrs/lemma /lemma lemmacomp }
    fi
    if [[ "$initial_input_attrs" != "* lex/" ]]; then
	initial_input_attrs="$initial_input_attrs lex/"
    fi
    input_attrs=$initial_input_attrs
else
    input_attrs="${initial_input_attrs/lemma /lemma lemmacomp } lex/"
fi


filter_new_attrs () {
    $cwb_describe_corpus -s $corpus |
    awk '
        BEGIN {
            for (i = 1; i < ARGC; i++) { attrs[i] = ARGV[i] }
            delete ARGV
        }
        /^p-ATT/ { old_attrs[$2] = 1 }
        END {
            for (i in attrs) {
                attrname_bare = gensub (/\//, "", "g", attrs[i])
                # Lemma needs to be recoded as lemmacomp if lemmacomp is
                # not already present
                if (! (attrname_bare in old_attrs) \
                    || (attrname_bare == "lemma" \
                        && ! ("lemmacomp" in old_attrs))) {
                    print attrs[i]
                }
            }
        }' $@
}

new_attrs=$(filter_new_attrs "$input_attrs")


time_stage () {
    time_cmd --format "- CPU time used: %U %R" "$@"
}

# Run a single stage function (name) after printing the description
# (descr). If function test_skip_$name is defined and its output is
# non-empty, skip the stage.
run_stage () {
    local name=$1
    shift
    local descr="$@"
    if type -t "test_skip_$name" > /dev/null; then
	msg=$(test_skip_$name)
	if [ "x$msg" != "x" ]; then
	    echo_verb "(Skipping ${descr,}: $msg)"
	    return
	fi
    fi
    echo_verb "$descr"
    time_stage exit_on_error $name
}

# Run all the stages in $stages sequentially.
run_stages () {
    local stagecnt=${#stages[*]}
    local i=0
    while [ $i -lt $stagecnt ]; do
	run_stage ${stages[$i]} "${stages[$(($i + 1))]}"
	i=$(($i + 2))
    done
}


# Stage functions and their descriptions
stages=(
    add_new_attrs "Adding lemgrams and lemmas without compound boundaries"
    cwb_encode "Encoding the new attributes"
    add_registry_attrs "Adding the new attributes to the corpus registry"
    cwb_make "Indexing and compressing the new attributes"
    extract_lemgrams "Extracting lemgrams for the database"
    extract_wordpict_rels
    "Extracting word picture relations for the database"
    add_name_attrs "Adding name attributes"
    import_database "Importing data to the MySQL database"
)


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

filter_attrs () {
    _grep_opts="$1"
    shift
    echo "$@" |
    tr ' ' '\n' |
    grep -En $_grep_opts |
    grep -E ":($(echo $new_attrs | sed -e 's/ /|/g'))/?\$"
}

add_new_attrs () {
    # Skip empty lines in the input VRT, in order to avoid a differing
    # number of tokens from the already encoded attributes (assuming
    # that cwb-encode was told to skip empty lines).
    comprcat "${input_files[@]}" |
    grep -v '^$' |
    add_lemmas_without_boundaries |
    add_lemgrams > $vrt_file
    if [ $? != 0 ]; then
	exit_on_error false
    fi
}

test_skip_add_new_attrs () {
    if [ "x$augmented_vrt_input" != x ]; then
	echo "already in input"
	comprcat "${input_files[@]}" > $vrt_file
    fi
}

cwb_encode_base () {
    _attrs=$1
    _is_featset=$2
    attrnames=$(echo $_attrs | sed -e 's/[0-9][0-9]*://g')
    attrnums=$(echo $_attrs | sed -e 's/:[^ ]*//g' | tr ' ' ',')
    convert_chars_opts=
    featset_text=
    if [ "x$_is_featset" != x ]; then
	featset_attrnums=$(
	    echo $(seq $(echo "$attrnames" | wc -w)) |
	    tr ' ' ','
	)
	convert_chars_opts="--feature-set-attrs $featset_attrnums"
	featset_text="feature-set "
    fi
    echo_verb Encoding $featset_text p-attributes: $attrnames
    egrep -v '^<' $vrt_file |
    cut -d'	' -f$attrnums |
    $vrt_convert_chars $convert_chars_opts |
    $cwb_encode -d $corpus_root/data/$corpus -p - -xsB -c utf8 \
	$(add_prefix "-P " $attrnames)
}

cwb_encode () {
    attrs_base=$(filter_attrs "-v /|:word\$" "word $input_attrs")
    attrs_featset=$(filter_attrs "/" "word $input_attrs")
    cwb_encode_base "$attrs_base"
    if [ "x$attrs_featset" != x ]; then
	cwb_encode_base "$attrs_featset" featset
    fi
    # exit 1
}

test_skip_cwb_encode () {
    [ "x$new_attrs" = x ] && echo "already present"
}

add_registry_attrs () {
    regfile=$cwb_regdir/$corpus
    cp -p $regfile $regfile.bak
    grep '^ATTRIBUTE ' $regfile | cut -d' ' -f2 > $tmp_prefix.old_attrs
    # Interleave the old and new attributes
    all_attrs=$(
	echo "word $input_attrs" |
	tr -d '/' |
	tr ' ' '\n' |
	diff -U100 $tmp_prefix.old_attrs - |
	grep -Ev '^(---|\+\+\+|@@)' |
	cut -c2-
    )
    sed -e '/^ATTRIBUTE word/ a'"$(add_prefix '\
ATTRIBUTE ' $all_attrs)" -e '/^ATTRIBUTE/ d' $regfile.bak > $regfile
}

test_skip_add_registry_attrs () {
    test_skip_cwb_encode
}

cwb_make () {
    $cwb_make -V $corpus
}

test_skip_cwb_make () {
    test_skip_cwb_encode
}

extract_lemgrams () {
    $vrt_extract_lemgrams --corpus-id $corpus < $vrt_file |
    gzip > $tsvdir/${corpus}_lemgrams.tsv.gz
}

test_skip_extract_lemgrams () {
    [ -s $tsvdir/${corpus}_lemgrams.tsv.gz ] && echo "already extracted"
}

extract_wordpict_rels () {
    $run_extract_rels --corpus-name $corpus \
	--input-fields "word ${input_attrs%/}" \
	--output-dir "$tsvdir" --relation-map "$wordpict_relmap" \
	--optimize-memory --no-tar \
	< $vrt_file
}

test_skip_extract_wordpict_rels () {
    if [ "x$wordpicture" = x ]; then
	echo "requested not to extract"
    elif [ -s $tsvdir/${corpus}_rels.tsv.gz ]; then
	echo "already extracted"
    fi
}

add_name_attrs () {
    $vrt_add_name_attrs $corpus @data @data
}

test_skip_add_name_attrs () {
    if [ "x$name_attrs" = x ]; then
	echo "not requested"
    elif corpus_has_attr $corpus s ne_ex; then
	echo "already present"
    fi
}

import_database () {
    tsv_files=$tsvdir/${corpus}_lemgrams.tsv.gz
    if [ "x$wordpicture" != x ]; then
	tsv_files="$tsv_files $(echo $tsvdir/${corpus}_rels*.tsv.gz)"
    fi
    $korp_mysql_import --prepare-tables --relations-format new $tsv_files
}

test_skip_import_database () {
    [ "x$import_database" = x ] &&
    echo "not requested"
}


main () {
    echo_verb "Adding parse information to Korp corpus $corpus:"
    set -o pipefail
    run_stages
    echo_verb "Completed."
}


# FIXME: The format is not effective, since the formats used in inner
# time_cmd calls take overwrite the format (TIMEFORMAT environment
# variable).
time_cmd --format "- Total CPU time used: %U %R" main "$@"
