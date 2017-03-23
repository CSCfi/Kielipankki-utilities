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
omit-attribute-comment
    omit the comment listing the positional attributes shown at the top of
    the output VRT
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

struct_attrs_lines=$(echo $struct_attrs | tr ' ' '\n')
struct_attrs_multi=$(
    echo "$struct_attrs_lines" | sort | sed -e 's/_.*//' | uniq -d)
# Filter out structural attributes without values (corresponding to
# XML tags without attributes) if they also occur with a value (XML
# tags with attributes), since the tag will be output anyway and so
# that process_tags_multi needs not take into account attributes
# without values.
struct_attrs=$(
    echo "$struct_attrs_lines" |
    perl -e '$r = "^(" . join("|", qw('"$struct_attrs_multi"')) . ")\$";
             while (<>) { print if ($_ !~ $r); }'
)

attr_opts="$(add_prefix '-P ' $pos_attrs) $(add_prefix '-S ' $struct_attrs)"

if [ "${struct_attrs#*_}" != "$struct_attrs" ]; then
    if [ "x$struct_attrs_multi" != x ]; then
	process_tags=process_tags_multi
    else
	process_tags=process_tags_single
    fi
else
    process_tags=cat
fi

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

if [ "x$omit_attribute_comment" = x ]; then
    add_attribute_comment=add_attribute_comment
else
    add_attribute_comment=cat
fi

process_tags_single () {
    # This is somewhat faster than using sed, but not significantly
    # faster than process_tags_multi below
    perl -pe 's/^(<[^\/_\s]*)_([^ ]*) ([^>]*)>/$1 $2="$3">/;
              s/^(<\/[^_]*)_.*>/$1>/;'
}

process_tags_multi () {
    perl -ne '
        BEGIN {
            $prevtag = $tag = $attrs = "";
        }
        if (/^(<[^\/_\s]*)_([^ ]*) ([^>]*)>/) {
            $tag = $1;
            if ($tag ne $prevtag && $attrs) {
                print "$prevtag$attrs>\n";
                $attrs = "";
            }
            $prevtag = $tag;
            $attrs .= " $2=\"$3\"";
        } elsif (/^(<\/[^_]*)_.*>/) {
            $tag = $1;
            if ($tag ne $prevtag) {
                print "$tag>\n";
            }
            $prevtag = $tag;
        } else {
            if ($prevtag && $attrs) {
                print "$prevtag$attrs>\n";
            }
            $tag = $prevtag = $attrs = "";
            print;
        }'
}

add_attribute_comment () {
    gawk 'NR == 1 {
              if (/^<\?xml/) { print }
              print "<!-- Positional attributes: '"$pos_attrs"' -->";
              if (/^<\?xml/) { next }
          }
          { print }'
}

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
    $process_tags |
    eval "$head_filter" |
    $tail_filter |
    $add_attribute_comment > $outfile
}


for corp in $corpora; do
    extract_vrt $corp
done
