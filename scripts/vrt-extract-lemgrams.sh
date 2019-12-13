#! /bin/sh
# -*- coding: utf-8 -*-


export LC_ALL=C

progname=`basename $0`
progdir=`dirname $0`


usage_header='$progname [options] [input.vrt ...]

Extract lemgram frequency information from VRT input and output the
data in a TSV format suitable for importing to the lemgram_index
table of the Korp MySQL database.'

optspecs='
corpus-id|corpus-name=CORPUS
    Korp corpus identifier is CORPUS (required).
lemgram-field=FIELD_NUM "-1" lemgram_fieldnr
    Extract lemgrams from the positional attribute number FIELD_NUM.
prefix-field=FIELD_NUM prefix_fieldnr
    Extract prefixes from the positional attribute number FIELD_NUM.
suffix-field=FIELD_NUM suffix_fieldnr
    Extract suffixes from the positional attribute number FIELD_NUM.
'

usage_footer='If FIELD_NUM is empty or not specified, do not extract the information
in question. If FIELD_NUM is negative, count from the end (the last
attribute is -1).'

. $progdir/korp-lib.sh


# Process options
eval "$optinfo_opt_handler"


if [ "x$corpus_id" = x ]; then
    error "Please specify a corpus id with --corpus-name"
fi


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
    vrt_decode_special_chars --no-xml-entities |
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
