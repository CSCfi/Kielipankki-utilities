#! /bin/sh
# -*- coding: utf-8 -*-

# Usage: vrt-sort-texts.sh [options] [input.vrt] > output.vrt


progname=`basename $0`
progdir=`dirname $0`


usage_header="Usage: $progname [options] [input.vrt] > output.vrt

Sort the text elements in a VRT file based on an attribute.

Note that the input may have an element spanning the whole input containing
the text elements but no elements that span multiple text elements but not all
of them."

optspecs='
attribute=ATTR attrname
order-from-corpus=CORPUS_ID order_corpus
transform=TRANSFORM * { add_transform "$1" }
'

. $progdir/korp-lib.sh


transforms=

add_transform () {
    transforms="$transforms
\$key =~ $1;"
}


# Process options
eval "$optinfo_opt_handler"


if [ "x$attrname" = "x" ]; then
    error "Please specify the sort attribute via --attribute"
fi


order_file=$tmp_prefix.order

read_order_from_corpus () {
    $cwb_bindir/cwb-s-decode -n $order_corpus -S text_$attrname > $order_file
}

add_sort_keys () {
    map_key_code=
    if [ "x$order_corpus" != "x" ]; then
	read_order_from_corpus
	begin_code='
	    open (my $orderf, "<", "'"$order_file"'")
		or die ("Cannot open file: $!");
	    %order = ();
	    while ($key = <$orderf>) {
		chomp;
                '"$transforms"'
		$order{$key} = $.;
	    }
            $keylen = length ($. + 1);
            $post_key = sprintf ("%0*d", $keylen, $. + 1);
	    close ($orderf);
            $pre_key = sprintf ("%0*d", $keylen, 0);
            for $key (keys (%order)) {
                $order{$key} = sprintf ("%0*d", $keylen, $order{$key});
            }'
	map_key_code='$key = $order{$key};'
    else
	begin_code='
            $pre_key = "";
            $post_key = "\xef\xbf\xbf"    # U+FFFF in UTF-8'
    fi
    perl -ne '
        BEGIN {
            '"$begin_code"'
        }
	if (/^<text.* '$attrname'="(.+?)"/) {
	    $key = $1;
           '"$transforms"'
            '"$map_key_code"'
            $text_seen = 1;
            $in_text = 1;
	} elsif (/^<\/text>/) {
            $in_text = 0;
        } elsif (! $in_text && /^</) {
            $key = ($text_seen ? $post_key : $pre_key);
        }
	print "$key\t$_"'
}


comprcat --files "*.vrt" "$@" |
add_sort_keys |
LC_ALL=C sort -t"$tab" -k1,1 -s |
cut -d"$tab" -f2-
