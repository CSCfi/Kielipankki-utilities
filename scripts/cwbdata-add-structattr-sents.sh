#! /bin/sh
# -*- coding: utf-8 -*-


# TODO:
# - Add sanity checks, e.g. that the number of structures match in the
#   input and the existing corpus.


progname=`basename $0`
progdir=`dirname $0`

usage_header="Usage: $progname [options] corpus [input ...]

Add (encode) CWB structural attributes to an already encoded corpus by joining
with a space the values of a positional attribute in the input.

Typically you first extract attribute information using
cwbdata-extract-structattr-sents.sh, tokenize and parse the output and then
add a new attribute, for example the lemmas of a text title."

optspecs='
struct-name|struct-attribute-name|element-name=STRUCT "text"
    add the attribute to structural attribute (element) STRUCT that is also in
    the input; the input elements may contain attributes "count" specifying
    the number of adjacent structures to which to add the value
attribute-name=ATTRNAME attr_name
    add the attribute named ATTRNAME
input-attribute-number=ATTRNUM "3" input_attrnum
    join the values of the positional attribute number ATTRNUM
'


. $progdir/korp-lib.sh


cwb_s_decode=$cwb_bindir/cwb-s-decode
cwb_s_encode=$cwb_bindir/cwb-s-encode
encode_special_chars="$progdir/vrt-convert-chars.py --encode"


# Process options
eval "$optinfo_opt_handler"


main () {
    local corpus structpos_fifo pid
    corpus=$1
    if [ "x$corpus" = x ]; then
	error "Please specify corpus id as the first argument"
    fi
    shift
    if [ "x$attr_name" = x ]; then
	error "Please specify attribute name via --attribute-name"
    fi
    structpos_fifo=$tmp_prefix.structpos.fifo
    if [ ! -p $structpos_fifo ]; then
	mkfifo $structpos_fifo
    fi
    $cwb_s_decode $corpus -S $struct_name > $structpos_fifo &
    pid=$!
    comprcat "$@" |
    perl -ne '
        BEGIN {
            $struct_name = $ARGV[0];
            $attrnum = $ARGV[1] - 1;
            @ARGV = ();
        }
        if (/^<$struct_name/) {
            ($start, $end, $count) =
                /.* start="(\d+)".* end="(\d+)".*?(?: count="(\d+)")?/;
            $count //= 1;
            @vals = ();
        } elsif (/^<\/$struct_name>/) {
            $attrval = join (" ", @vals) . "\n";
            for $i (1 .. $count) {
		print $attrval;
	    }
        } elsif (! /^</) {
            chomp;
            @attrs = split (/\t/);
            push (@vals, $attrs[$attrnum]);
        }
    ' $struct_name $input_attrnum |
    $encode_special_chars |
    paste $structpos_fifo - |
    $cwb_s_encode -d $corpus_root/data/$corpus -B -c utf8 \
    	-V ${struct_name}_$attr_name
    wait $pid
    cwb_registry_add_structattr $corpus $struct_name $attr_name
}


main "$@"
