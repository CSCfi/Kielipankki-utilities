#! /bin/sh
# -*- coding: utf-8 -*-


export LC_ALL=C

progname=`basename $0`

tmpdir=${TMPDIR:-${TEMPDIR:-${TMP:-${TEMP:-/tmp}}}}
tmp_prefix=$tmpdir/$progname.$$

special_chars=" /<>|"
encoded_special_char_offset=0x7F
encoded_special_char_prefix=

corpus_id=
lemgram_fieldnr=-1
prefix_fieldnr=
suffix_fieldnr=


warn () {
    echo "$progname: Warning: $1" >&2
}

error () {
    echo "$progname: $1" >&2
    exit 1
}

usage () {
    cat <<EOF
Usage: $progname [options] [file ...]
EOF
    exit 0
}

cleanup () {
    if [ "x$tmp_prefix" != "x" ]; then
	: # rm -f "$tmp_prefix.*"
    fi
}

cleanup_abort () {
    cleanup
    exit 1
}


trap cleanup 0
trap cleanup_abort 1 2 13 15


# Test if GNU getopt
getopt -T > /dev/null
if [ $? -eq 4 ]; then
    # This requires GNU getopt
    args=`getopt -o "h" -l "help,corpus-id:,corpus-name:,lemgram-field:,prefix-field:,suffix-field:" -- "$@"`
    if [ $? -ne 0 ]; then
	exit 1
    fi
    eval set -- "$args"
fi
# If not GNU getopt, arguments of long options must be separated from
# the option string by a space; getopt allows an equals sign.

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	--corpus-id | --corpus-name)
	    shift
	    corpus_id=$1
	    ;;
	--lemgram-field )
	    shift
	    lemgram_fieldnr=$1
	    ;;
	--prefix-field )
	    shift
	    prefix_fieldnr=$1
	    ;;
	--suffix-field )
	    shift
	    suffix_fieldnr=$1
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

if [ "x$corpus_id" = x ]; then
    error "Please specify a corpus id with --corpus-name"
fi

decode_special_chars () {
    perl -CSD -e '
        use feature "unicode_strings";
	$sp_chars = "'"$special_chars"'";
	%sp_char_map = map {("'$encoded_special_char_prefix'"
	                     . chr ('$encoded_special_char_offset' + $_))
			    => substr ($sp_chars, $_, 1)}
			   (0 .. length ($sp_chars));
	while (<>)
	{
	    for $c (keys (%sp_char_map))
	    {
		s/$c/$sp_char_map{$c}/g;
	    }
            s/&quot;/"/g;
            s/&amp;/&/g;
            s/&apos;/'"'"'/g;
            s/&lt;/</g;
            s/&gt;/>/g;
	    print;
	}'
}

extract_lemgrams () {
    fieldnr=$1
    if [ "x$fieldnr" = x ]; then
	return
    fi
    if [ $fieldnr -lt 0 ]; then
	fieldnr='(NF - '`expr $fieldnr + 1`')'
    fi
    fieldtype=$2
    shift
    shift
    if [ "$#" != "0" ]; then
	cat "$@"
    else
	cat
    fi |
    grep -Ev '^<' |
    awk -F'	' '{print $'"$fieldnr"'}' |
    tr '|' '\n' |
    grep -Ev '^(.*:[0-9]+)?$' |
    perl -ne 'chomp; print "$_\t'$fieldtype'\n"'
}

combine_lemgrams () {
    corpname_u=`echo $corpus_id | sed 's/.*/\U&\E/'`
    sort |
    uniq -c |
    decode_special_chars |
    perl -e '
	$token = $prev_token = "";
	@freqs = ("0", "0", "0");
	sub output {
	    printf "%s\t%s\t%s\t%s\t'$corpname_u'\n", $prev_token, @freqs;
	}
	while (<>) {
	    ($freq, $token, $type) = /^\s*(\d+)\s+(.+?)\t(.+)$/;
	    if ($prev_token && $token ne $prev_token) {
		output ();
		@freqs = ("0", "0", "0");
	    }
	    $freqs[$type] = $freq;
	    $prev_token = $token;
	}
	output ();'
}

make_lemgrams_tsv () {
    (
	extract_lemgrams "$lemgram_fieldnr" 0 "$@"
	extract_lemgrams "$prefix_fieldnr" 1 "$@"
	extract_lemgrams "$suffix_fieldnr" 2 "$@"
    ) |
    combine_lemgrams
}

if [ "$#" = 0 ]; then
    cat > "$tmp_prefix.in"
    set -- "$tmp_prefix.in"
fi

make_lemgrams_tsv "$@"
