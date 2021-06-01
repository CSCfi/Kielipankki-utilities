#! /bin/sh

# A simpler and faster alternative to cwbdata2vrt.py


progname=`basename $0`
progdir=`dirname $0`

usage_header="Usage: $progname [options] corpus_id ...

Generate a VRT file from each corpus specified as an argument, based on its
data stored in CWB.

The output is XML-compatible, except for possible crossing elements. By
default, the output contains only the positional attribute 'word' and the
structural attributes 'text' and 'sentence'.

The output has the encoded special characters unencoded; <, > and &
XML-encoded everywhere and \" XML-encoded in structural attribute values.

The corpus ids specified may contain shell wildcards that are expanded."

optspecs='
positional-attributes|pos-attrs=ATTRLIST "word" pos_attrs
    output the positional attributes listed in ATTRLIST, separated by spaces
structural-attributes|struct-attrs=ATTRLIST "text sentence" struct_attrs
    output the structural attributes listed in ATTRLIST, separated by spaces
all-attributes|all all_attrs
    output all positional and structural attributes in the corpora
sort-structural-attributes|sort sort_struct_attrs
    sort structural attribute annotations ("XML attributes") alphabetically,
    instead of using their order of declaration in the registry file
undef-value|replace-undef=REPL
    replace all "__UNDEF__" (undefined) values of all positional attributes
    with REPL; if the value set of any positional attribute of any corpus
    contains both "__UNDEF__" and REPL, no VRT files are generated unless
    --force-undef-value is specified
force-undef-value|force-replace-undef force_undef
    replace "__UNDEF__" values with the value specified with --undef-value
    even if the value set of an attribute contains both "__UNDEF__" and the
    replacement value
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
	process_tags=cat_noargs
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

# Check if any positional attribute of any corpus contains both
# __UNDEF__ and the replacement value; if so, abort unless
# --force-undef-value has been specified. (Another option would be to
# check this one corpus at a time and refuse to generate VRT output
# only for the corpora with attributes with both __UNDEF__ and
# replacement value. However, as the input corpora for a single run
# are often subcorpora of the same corpus or otherwise related, it is
# justified to produce output for either all or none of the corpora.)
check_undef_replacement () {
    local undef_value corpus attr msg_base abort
    abort=
    undef_value=$1
    shift
    for corpus in "$@"; do
        for attr in $(corpus_list_attrs $corpus p); do
            if corpus_posattr_contains_values $corpus $attr "__UNDEF__" &&
                    corpus_posattr_contains_values $corpus $attr "$undef_value";
            then
                msg_base="corpus $corpus: the value set of positional attribute $attr contains both \"__UNDEF__\" and its replacement \"$undef_value\""
                if [ "x$force_undef" != x ]; then
                    warn "$msg_base; replacing anyway, as --force-undef-value was specified"
                else
                    warn "$msg_base"
                    abort=1
                fi
            fi
        done
    done
    if [ "x$abort" != x ]; then
        error "Aborting as the value set of at least one positional attribute of at least one corpus contains both \"__UNDEF__\" and its replacement \"$undef_value\"; specify --force-undef-value to replace anyway"
    fi
}

# Perl code snippets used in both process_tags_single and
# process_tags_multi

# Encode & and " as XML character references in structural attribute
# values, as cwb-encode -Cx appears not to do that. If cwb-encode is
# ever changed to do that, this will have to be removed. Encoding <
# and > is handled by vrt_decode_special_chars in shlib/vrt.sh.
perl_encode_entities_attrval='
    $attrval =~ s/&/&amp;/g;
    $attrval =~ s/"/&quot;/g;
'
# Decode &quot; and &apos; in tokens (positional attributes), as they
# need not be encoded there but they are encoded by cwb-encode -Cx.
perl_decode_entities_token='
    s/&quot;/"/g;
    s/&apos;/'"'"'/g;
'
# Optionally replace __UNDEF__ values with the string given with
# --undef-value.
perl_replace_undef=
if [ "x$undef_value" != x ]; then
    check_undef_replacement "$undef_value" $corpora
    perl_replace_undef='
        s/(?:\t|^)\K__UNDEF__(?=\t|$)/'"$undef_value"'/g;
'
fi

process_tags_single () {
    # This is somewhat faster than using sed, but not significantly
    # faster than process_tags_multi below
    perl -ne '
        if (/^(<[^\/_\s]*)_([^ ]*) ([^>]*)>/) {
	    # Structure start tag with annotation value
	    ($tag, $attrname, $attrval) = ($1, $2, $3);
	    '"$perl_encode_entities_attrval"'
	    print "$tag $attrname=\"$attrval\">\n";
	} else {
	    # Anything else
	    s/^(<\/[^_]*)_.*>/$1>/;
	    if (! /^</) {
		'"$perl_decode_entities_token"'
                '"$perl_replace_undef"'
	    }
	    print;
	}
    '
}

# Perl code snippets depending on whether the structure annotations
# should be sorted or not. Using a list instead of a string does not
# seem to be significantly slower, so maybe we could have only the
# perl_attrs_get different (with or without sorting).
if [ "x$sort_struct_attrs" = x ]; then
    perl_attrs_clear='$attrs = ""'
    perl_attrs_append='$attrs .= " $attrname=\"$attrval\""'
    perl_attrs_get='$attrs'
else
    perl_attrs_clear='@attrs = ()'
    perl_attrs_append='push(@attrs, "$attrname=\"$attrval\"")'
    perl_attrs_get='" " . join (" ", sort { substr($a, 0, index($a, "=")) cmp
                                            substr($b, 0, index($b, "=")) }
                                          @attrs)'
fi

process_tags_multi () {
    local corp
    corp=$1
    perl -ne '
        BEGIN {
            $prevtag = $tag = "";
	    '"$perl_attrs_clear"';
	    $cpos = 0;
            $prevtag_printed = 0;
        }
        if (/^(<[^\/_\s]*)(?:_([^ ]*)( )?(.*))?>$/) {
	    # Structure start tag, possibly with an annotation value
            $tag = $1;
            if ($prevtag && $tag ne $prevtag && ! $prevtag_printed) {
                print "$prevtag" . '"$perl_attrs_get"' . ">\n";
                '"$perl_attrs_clear"';
            }
            $prevtag = $tag;
            $prevtag_printed = 0;
	    if ($2) {
		$attrname = $2;
		# If the annotation is defined but has no value, not
		# even an empty string (a line of the form
		# <struct_attr>), it is treated as an empty string.
		# Alternatively, we could have special value for such
		# undefined values, but they probably should not occur
		# anyway. One option might be to add (optionally) a
		# special VRT comment indicating the issue.
		if (! $3) {
		    $struct = substr($prevtag, 1);
		    print STDERR ("'"$progname"': Warning: corpus '"$corp"',"
		                  . " position $cpos: structure \"$struct\":"
				  . " undefined value for attribute"
				  . " \"$attrname\" treated as empty string\n");
		}
		$attrval = $4;
		'"$perl_encode_entities_attrval"'
		'"$perl_attrs_append"';
	    }
        } elsif (/^(<\/[^_]*)(_.*)?>/) {
	    # Structure end tag
            $tag = $1;
            if ($tag ne $prevtag) {
                print "$tag>\n";
                $prevtag_printed = 1;
            }
            $prevtag = $tag;
        } else {
	    # Token, XML declaration or <corpus> start tag
            if ($prevtag && ! $prevtag_printed) {
                print "$prevtag" . '"$perl_attrs_get"' . ">\n";
            }
            $tag = $prevtag = "";
            $prevtag_printed = 0;
	    '"$perl_attrs_clear"';
	    if (! /^</) {
	       	# Token
	        '"$perl_decode_entities_token"'
                '"$perl_replace_undef"'
		$cpos++;
	    }
            print;
        }
    '
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
    local corp timestamp fullname userinfo version freetext command args
    corp=$1
    timestamp="Time: $(get_isodate)"
    # https://stackoverflow.com/a/833256
    fullname="$(getent passwd $USER | cut -d: -f5 | cut -d, -f1)"
    userinfo="User: $USER@$(hostname -f) ($fullname)"
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
    # $process_tags needs to precede vrt_decode_special_chars;
    # otherwise it would encode the & in the &lt; and &gt; produced by
    # the latter.
    $cwb_bindir/cwb-decode -Cx $corp $attr_opts |
    $process_tags $corp |
    vrt_decode_special_chars --xml-entities |
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
