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
all-attributes|all all_attrs
    output all positional and structural attributes in the corpora
include-xml-declaration
    include XML declaration in the output (omitted by default)
include-corpus-element
    include in the output the top-level "corpus" element added by cwb-decode
    (omitted by default)
omit-attribute-comment
    omit the comment listing the positional attributes shown at the top of
    the output VRT
omit-log-comment
    omit the comment containing information about the run of the script
vrt-file-name-template|output-file=FILE "{corpid}.vrt" outfile_templ
    write the output VRT to file named FILE, where {corpid} is replaced
    with the corpus id; FILE may contain a directory part as well; possible
    non-existent directories are created; use - to write to standard output
overwrite|force
    overwrite output VRT file if it already exists; by default, do not
    overwrite
v|verbose
    output progress information to standard output (standard error if the
    VRT output is written to standard output)
'

. $progdir/korp-lib.sh

# Process options
eval "$optinfo_opt_handler"


if [ "x$1" = x ]; then
    error "Please specify corpora"
fi

corpora=$(list_corpora "$@")

if [ "x$all_attrs" != x ]; then
    struct_attrs=
    pos_attrs=
    attr_opts=-ALL
    process_tags=process_tags_multi
else
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

if [ "x$omit_attribute_comment" = x ] || [ "x$omit_log_comment" = x ]; then
    add_vrt_comments=prepend_vrt_comments
else
    add_vrt_comments=cat_noargs
fi

cat_noargs () {
    # Ignore possible arguments
    cat
}

# Encode &, <, > and " as XML character references in structural
# attribute values, as cwb-encode -Cx appears not to do that. If
# cwb-encode is ever changed to do that, this will have to be removed.
perl_make_entities='
    $attrval =~ s/&/&amp;/g;
    $attrval =~ s/</&lt;/g;
    $attrval =~ s/>/&gt;/g;
    $attrval =~ s/"/&quot;/g;
'

process_tags_single () {
    # This is somewhat faster than using sed, but not significantly
    # faster than process_tags_multi below
    perl -ne '
        if (/^(<[^\/_\s]*)_([^ ]*) ([^>]*)>/) {
	    ($tag, $attrname, $attrval) = ($1, $2, $3);
	    '"$perl_make_entities"'
	    print "$tag $attrname=\"$attrval\">\n";
	} else {
	    s/^(<\/[^_]*)_.*>/$1>/;
	    print;
	}
    '
}

process_tags_multi () {
    perl -ne '
        BEGIN {
            $prevtag = $tag = $attrs = "";
        }
        if (/^(<[^\/_\s]*)(?:_([^ ]*) (.*))?>$/) {
            $tag = $1;
            if ($tag ne $prevtag && $attrs) {
                print "$prevtag$attrs>\n";
                $attrs = "";
            }
            $prevtag = $tag;
	    if ($2) {
		$attrname = $2;
		$attrval = $3;
		'"$perl_make_entities"'
		$attrs .= " $attrname=\"$attrval\"";
	    }
        } elsif (/^(<\/[^_]*)(_.*)?>/) {
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

prepend_vrt_comments () {
    # Each comment is an argument of its own; empty arguments are
    # excluded
    awk '
        BEGIN {
	    for (i = 1; i < ARGC; i++) {
	        if (ARGV[i]) {
	            comments[i] = ARGV[i]
		}
            }
            ARGC = 0
        }
	NR == 1 {
	    if (/^<\?xml/) { print }
            for (i in comments) {
	        print "<!-- #vrt " comments[i] " -->"
	    }
	    if (/^<\?xml/) { next }
	}
	{ print }
    ' "$@"
}

get_isodate () {
    date +'%Y-%m-%d %H:%M:%S %z'
}

make_log_info () {
    # This imitates a proposal for the VRT Tools log comment format,
    # which is still subject to change (2019-09-20)
    local corp timestamp userinfo version freetext command args
    corp=$1
    timestamp="Time: $(get_isodate)"
    userinfo="User: $USER@$HOSTNAME"
    # What should be the version, if any?
    version="Version: FIN-CLARIN corpus processing scripts (undefined version)"
    descr="Description: Generated VRT from CWB data for corpus \"$corp\""
    script="Script: $(basename $0)"
    args="Arguments: $cmdline_args_orig"
    echo "process-log: BEGIN"
    printf "%s\n" "process-log: $timestamp | $descr | $script | $args | $version | $userinfo"
    echo "process-log: END"
}

make_vrt_comments () {
    awk '{print "<!-- #vrt " $0 " -->"}'
}

extract_vrt () {
    local corp verbose_msg outfile dirname head_comment head_comment2 attr_comment
    corp=$1
    verbose_msg="Writing VRT output of corpus $corp to"
    if [ "x$outfile_templ" != "x-" ]; then
	outfile=$(echo "$outfile_templ" | sed -e "s/{corpid}/$corp/g")
	if [ -e "$outfile" ] && [ "x$overwrite" = x ]; then
	    warn "Skipping corpus $corp: output file $outfile already exists"
	    return
	fi
	if [ ! -e "$outfile" ]; then
	    dirname=$(dirname "$outfile")
	    mkdir -p "$dirname" 2> $tmp_prefix.err
	    if [ $? != 0 ]; then
		warn "Skipping corpus $corp: $(sed -e 's/^mkdir: //' $tmp_prefix.err)"
		return
	    fi
	fi
	touch "$outfile" 2> $tmp_prefix.err
	if [ $? != 0 ]; then
	    warn "Skipping corpus $corp: cannot write to output file $outfile"
	    return
	fi
	echo_verb "$verbose_msg file $outfile"
	if [ "x$overwrite" != x ] && [ -e "$outfile" ]; then
	    verbose warn "Overwriting existing file $outfile as requested"
	fi
    else
	outfile=/dev/stdout
	echo_verb "$verbose_msg standard output" >&2
    fi
    if [ "x$all_attrs" != x ]; then
	# Use echo to get the attribute names on the same line,
	# separated by spaces
	pos_attrs=$(echo $(corpus_list_attrs --feature-set-slash $corp p))
    fi
    if [ "x$omit_log_comment" = x ]; then
	head_comment="info: VRT generated from CWB data for corpus \"$corp\" ($(get_isodate))"
	head_comment2="info: A processing log at the end of file"
    fi
    if [ "x$omit_attribute_comment" = x ]; then
	attr_comment="positional-attributes: $pos_attrs"
    fi
    $cwb_bindir/cwb-decode -Cx $corp $attr_opts |
    vrt_decode_special_chars --xml-entities |
    $process_tags |
    eval "$head_filter" |
    $tail_filter |
    $add_vrt_comments "$attr_comment" "$head_comment" "$head_comment2" > $outfile
    if [ "x$omit_log_comment" = x ]; then
	make_log_info $corp | make_vrt_comments >> $outfile
    fi
}


for corp in $corpora; do
    extract_vrt $corp
done
