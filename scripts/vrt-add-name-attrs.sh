#! /bin/bash
# -*- coding: utf-8 -*-

# Usage: vrt-add-name-attrs.sh [options] corpus_id base_vrt name_vrt

# Requires Bash because of using process substitution


progname=`basename $0`
progdir=`dirname $0`


shortopts="h"
longopts="help,vrt-dir:,skip-encode,no-encode,force"

. $progdir/korp-lib.sh

vrtdir=
encode=1
force=

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
  --no-encode
  --force
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
	--no-encode )
	    encode=
	    ;;
	--force )
	    force=1
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

if [ -e "$datadir/${ne_struct}_name.avs" ]; then
    printf "Name attributes seem to already exist in corpus $corpus; "
    if [ "x$force" != x ]; then
	echo "regenerating them because --force was specified"
    else
	echo "please specify --force to regenerate"
	exit 1
    fi
fi


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

make_names_vrt () {
    mkdir -p "$vrtdir"
    paste <(get_wordform_lemma) <(get_nertag) |
    gawk -F"$tab" '/^</ || NF == 3' |
    $progdir/vrt-convert-name-attrs.py --word-field=1 --lemma-field=2 \
	--nertag-field=3 --output-fields=1,3 --add-bio-attribute \
	> "$names_vrt_file"
}

encode () {
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
    cwb_index_posattr $corpus $attr_nertag $attr_bio > /dev/null
}


make_names_vrt
if [ "x$encode" != x ]; then
    encode
    add_registry_attrs
    index_posattrs
fi
gzip -f "$names_vrt_file"
