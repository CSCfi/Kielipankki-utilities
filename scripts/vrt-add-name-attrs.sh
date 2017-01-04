#! /bin/bash
# -*- coding: utf-8 -*-

# Usage: vrt-add-name-attrs.sh [options] corpus_id base_vrt name_vrt

# Requires Bash because of using process substitution


progname=`basename $0`
progdir=`dirname $0`


shortopts="h"
longopts="help,vrt-dir:,text-sort-attribute:,verify-order,skip-encode,no-encode,force,verbose"

. $progdir/korp-lib.sh

vrtdir=
sort_attr=
output_input_structs=
verify_order=
encode=1
force=
verbose=

ne_struct=ne
ne_attrs="name fulltype ex type subtype placename placename_source"
attr_nertag=nertag
attr_bio=nerbio


usage () {
    cat <<EOF
Usage: $progname [options] corpus_id {base_vrt_file | @data}
                 {name_vrt_file | @data}

Add name attributes as structural attributes ne and their data.

Filename @data: use existing CWB data.

Options:
  -h, --help      show this help
  --vrt-dir DIR
  --text-sort-attribute ATTRNAME
  --verify-order
  --no-encode
  --force
  --verbose
EOF
    exit 0
}

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	--vrt-dir )
	    shift
	    vrtdir=$1
	    ;;
	--text-sort-attribute )
	    shift
	    sort_attr=$1
	    output_input_structs=--output-input-structs
	    ;;
	--verify-order )
	    verify_order=1
	    ;;
	--no-encode )
	    encode=
	    ;;
	--force )
	    force=1
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


if [ "x$3" = "x" ]; then
    error "Required arguments are corpus id, base VRT file and name VRT file"
fi

corpus=$1
base_vrt=$2
name_vrt=$3

if [ "x$vrtdir" = x ]; then
    vrtdir=$corpus_root/vrt/$corpus
fi
datadir=$corpus_root/data/$corpus
names_vrt_file=$vrtdir/${corpus}_names.vrt
regfile=$cwb_regdir/$corpus

if [ "x$base_vrt" != "x@data" ]; then
    if [ ! -r "$base_vrt" ]; then
	error "Cannot read base VRT file $base_vrt"
    fi
else
    if [ ! -r "$datadir/word.corpus.cnt" ] &&
	[ ! -r "$datadir/lemma.corpus.cnt" ];
    then
	error "Cannot read CWB data files for base VRT"
    fi
fi
if [ "x$name_vrt" != "x@data" ]; then
    if [ ! -r "$name_vrt" ]; then
	error "Cannot read name VRT file $name_vrt"
    fi
else
    if [ ! -r "$datadir/$attr_nertag.corpus.cnt" ]; then
	error "Cannot read CWB data files for NER VRT"
    fi
fi

if [ -e "$datadir/${ne_struct}_name.avs" ]; then
    printf "Name attributes seem to exist already in corpus $corpus; "
    if [ "x$force" != x ]; then
	echo "regenerating them because --force was specified"
    else
	echo "please specify --force to regenerate"
	exit 1
    fi
fi


# TODO: The following two functions share much common; could the
# common part be extracted to a function of its own?

get_wordform_lemma () {
    if [ "$base_vrt" != "@data" ]; then
	comprcat --files "*.vrt" "$base_vrt" |
	cut -d"$tab" -f1,2
    else
	$cwb_bindir/cwb-decode -Cx $corpus -P word -P lemma |
	grep -v '^<'
    fi |
    $progdir/vrt-convert-chars.py --decode
}

get_nertag () {
    if [ "$name_vrt" != "@data" ]; then
	comprcat --files "*.vrt" "$name_vrt" |
	gawk -F"$tab" '/^</ {print ""; next} {print $NF}'
    else
	$cwb_bindir/cwb-decode -Cx $corpus -P $attr_nertag |
	grep -v '^<'
    fi |
    $progdir/vrt-convert-chars.py --decode
}

sort_names_vrt () {
    if [ "x$sort_attr" != "x" ]; then
	$progdir/vrt-sort-texts.sh --attribute $sort_attr \
	    --order-from-corpus $corpus
    else
	cat
    fi
}

make_names_vrt () {
    verbose echo_timestamp "Generating a VRT file with name data"
    mkdir -p "$vrtdir"
    paste <(get_wordform_lemma) <(get_nertag) |
    gawk -F"$tab" '/^</ || NF == 3' |
    $progdir/vrt-convert-name-attrs.py --word-field=1 --lemma-field=2 \
	--nertag-field=3 --output-fields=1,3 --add-bio-attribute \
	$output_input_structs |
    sort_names_vrt > "$names_vrt_file"
}

get_cwb_corpus_attr () {
    local corpus
    corpus=$1
    attr=$2
    $cwb_bindir/cwb-decode -Cx $corpus -P $attr |
    grep -v '^<' |
    # This may need to be changed if vrt-convert-chars.py --decode is
    # modified to encode at least the ampersand.
    sed -e 's/&apos;/'"'"'/g; s/&quot;/"/g; s/&amp;/\&/g' |
    $progdir/vrt-convert-chars.py --decode
}

verify_names_vrt_order () {
    verbose echo_timestamp "Verifying the order of corpus tokens"
    diff_file=$tmp_prefix.diff
    diff <(get_cwb_corpus_attr $corpus word) \
	<(grep -v '^<' "$names_vrt_file" | cut -d"$tab" -f1) > "$diff_file"
    if [ "$?" != "0" ]; then
	echo "Order of corpus tokens in the NER data differs from that in the encoded corpus:" > /dev/stderr
	cat "$diff_file" > /dev/stderr
	exit 1
    fi
}

encode () {
    verbose echo_timestamp "Encoding the name data for CWB"
    mkdir -p "$datadir"
    cut -d"$tab" -f2,3 "$names_vrt_file" |
    $progdir/vrt-convert-chars.py --encode |
    $cwb_bindir/cwb-encode -d "$datadir" -xsB -cutf8 \
	-p - -P $attr_nertag -P $attr_bio -S $ne_struct:0+${ne_attrs// /+} \
	-0 text -0 paragraph -0 sentence
}

add_registry_attrs () {
    # FIXME: This does not work correctly if the corpus already
    # contains only some of the attributes
    if [ ! -e "$regfile" ]; then
	warn "Registry file $regfile does not exist: cannot add name attributes to the registry"
    else
	if grep -q "STRUCTURE ${ne_struct}_name" "$regfile"; then
	    warn "Name attributes already appear to exist in registry file $regfile"
	else
	    cwb_registry_add_structattr $corpus $ne_struct $ne_attrs
	fi
	cwb_registry_add_posattr $corpus $attr_nertag $attr_bio
    fi
}

index_posattrs () {
    verbose echo_timestamp "Indexing and compressing the new positional attributes"
    cwb_index_posattr $corpus $attr_nertag $attr_bio > /dev/null
}


make_names_vrt
if [ "x$verify_order" != "x" ]; then
    verify_names_vrt_order
fi
if [ "x$encode" != x ]; then
    encode
    add_registry_attrs
    index_posattrs
fi
verbose echo_timestamp "Compressing the names VRT file"
gzip -f "$names_vrt_file"
verbose echo_timestamp "Done"
