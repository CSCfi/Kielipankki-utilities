#! /bin/sh

# A simpler and faster alternative to cwbdata2vrt.py


progname=`basename $0`
progdir=`dirname $0`

usage_header="Usage: $progname [options] corpus_id ...

Generate a VRT file from each corpus specified as an argument, based on its
data stored in CWB.

The output is XML-compatible, except for possible crossing elements. By
default, the output contains only the positional attribute 'word' and the
structural attributes 'text' and 'sentence'. The output has the encoded
special characters unencoded.

The corpus ids specified may contain shell wildcards that are expanded."

optspecs='
positional-attributes|pos-attrs=ATTRLIST "word" pos_attrs
    output the positional attributes listed in ATTRLIST, separated by spaces
structural-attributes|struct-attrs=ATTRLIST "text sentence" struct_attrs
    output the structural attributes listed in ATTRLIST, separated by spaces
include-xml-declaration
    include XML declaration in the output (omitted by default)
include-corpus-element
    include in the output the top-level "corpus" element added by cwb-decode
    (omitted by default)
vrt-file-name-template=FILE "{corpid}.vrt" outfile_templ
    write the output VRT to file named FILE, where {corpid} is replaced
    with the corpus id; FILE may contain a directory part as well
overwrite|force
    overwrite output VRT file if it already exists; by default, do not
    overwrite
v|verbose
    output progress information
'

. $progdir/korp-lib.sh

# Process options
eval "$optinfo_opt_handler"


if [ "x$1" = x ]; then
    error "Please specify corpora"
fi

corpora=$(list_corpora "$@")
attr_opts="$(add_prefix '-P ' $pos_attrs) $(add_prefix '-S ' $struct_attrs)"

if [ "x$include_corpus_element" = x ]; then
    if [ "x$include_xml_declaration" = x ]; then
	# No <corpus>...</corpus>, no <?xml...>
	head_filter="tail -n +3"
	tail_filter="head -n -1"
    else
	# No <corpus>...</corpus>, but <?xml...>
	# This needs to be eval'ed because of the space in the regex
	head_filter="grep -Ev '^<(corpus |/corpus>)'"
	tail_filter=cat
    fi
else
    if [ "x$include_xml_declaration" = x ]; then
	# <corpus>...</corpus>, no <?xml...>
	head_filter="tail -n +2"
    else
	# <corpus>...</corpus> and <?xml...>
	head_filter=cat
    fi
    tail_filter=cat
fi

extract_vrt () {
    local corp
    corp=$1
    outfile=$(echo "$outfile_templ" | sed -e "s/{corpid}/$corp/g")
    if [ -e "$outfile" ] && [ "x$overwrite" = x ]; then
	warn "Skipping corpus $corp: output file $outfile already exists"
	return
    fi
    echo_verb "Writing VRT output of corpus $corp to file $outfile"
    if [ "x$overwrite" != x ]; then
	verbose warn "Overwriting existing file $outfile as requested"
    fi
    $cwb_bindir/cwb-decode -Cx $corp $attr_opts |
    # This is faster than calling vrt-convert-chars.py --decode
    perl -CSD -pe 's/\x{007f}/ /g; s/\x{0080}/\//g; s/\x{0081}/&lt;/g; s/\x{0082}/&gt;/g; s/\x{0083}/|/g' |
    eval "$head_filter" |
    $tail_filter > $outfile
}


for corp in $corpora; do
    extract_vrt $corp
done
