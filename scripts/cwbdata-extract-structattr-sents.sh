#! /bin/sh
# -*- coding: utf-8 -*-


progname=`basename $0`
progdir=`dirname $0`

usage_header="Usage: $progname [options] corpus [...]

Extract from encoded CWB data values of structural attributes as sentences,
for example, for lemmatizing."

optspecs='
struct-name|struct-attribute-name|element-name=STRUCT
    take the attributes from structural attribute (element) STRUCT
sentence-attribute-names|sentence-attr-names=ATTRLIST sent_attrs
    extract attributes in ATTRLIST of STRUCT to a sentence; the attribute
    names in ATTRLIST are separated by spaces
extra-attribute-names|extra-attr-names=ATTRLIST *extra_attrs
    extract attributes in ATTRLIST from STRUCT and output them as attributes
    of the output structure; the attribute names in ATTRLIST are separated by
    spaces
output-text-struct=STRUCT "text" output_struct
    enclose the output of each input structure in STRUCT
output-sentence-structs output_sent
    output extracted sentences within <sentence> elements
'


. $progdir/korp-lib.sh


cwb_s_decode=$cwb_bindir/cwb-s-decode
decode_special_chars="$progdir/vrt-convert-chars.py --decode"


# Process options
eval "$optinfo_opt_handler"


extract_attrs () {
    local corpus attr attr_files
    corpus=$1
    $cwb_s_decode $corpus -S $struct_name > $tmp_prefix.structpos
    attr_files=
    for attr in $extra_attrs $sent_attrs; do
	$cwb_s_decode -n $corpus -S ${struct_name}_$attr \
	    > $tmp_prefix.attr.$attr
	attr_files="$attr_files $tmp_prefix.attr.$attr"
    done
    paste $tmp_prefix.structpos $attr_files |
    $decode_special_chars |
    perl -CSD -ne '
        BEGIN {
            @extra_attrs = @ARGV;
            $last_extra_attr = $#extra_attrs;
            @ARGV = ();
        }
        sub xml_encode {
            my ($s) = @_;
            # The data should not contain numeric XML character
            # references, so they should be fixed elsewhere.
            # $s =~ s/&\#(\d+);/chr($1)/ge;
            # $s =~ s/&\#x([0-9a-fA-f]+);/chr(hex($1))/ge;
            $s =~ s/&/\&amp;/g;
            $s =~ s/</\&lt;/g;
            $s =~ s/>/\&gt;/g;
            return $s;
        }
        chomp;
        @f = split ("\t");
        print "<'"$output_struct"' corpus=\"'"$corpus"'\" start=\"$f[0]\" end=\"$f[1]\"";
        for ($i = 0; $i <= $last_extra_attr; $i++) {
            $val = xml_encode ($f[$i + 2]);
            $val =~ s/\"/\&quot;/g;
            print " $extra_attrs[$i]=\"$val\"";
        }
        print ">\n";
        print join ("\n\n",
                    map {xml_encode ($_)} @f[($last_extra_attr + 3)..$#f]);
        print "\n</'"$output_struct"'>\n";
    ' $extra_attrs
}

main () {
    local corpus
    for corpus in "$@"; do
	extract_attrs $corpus
    done
}


main "$@"
