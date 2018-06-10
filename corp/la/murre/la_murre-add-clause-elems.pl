#! /usr/bin/perl -nw
# -*- coding: utf-8 -*-

# Add to VRT files non-nested clause elements based on possibly nested
# cl elements.
#
# Usage: $progname [--remove-cl] < input.vrt > output.vrt
#
# The clause elements inherit the attributes of the corresponding cl
# elements. In addition, they get the attributes "depth" for cl
# nesting depth and "partnum" for the number of the clause element
# corresponding to a part of the cl element (the clause elements for a
# single cl element may be interrupted by nested cl elements).
#
# If --remove-cl is specified, remove the original cl elements.


BEGIN {
    $print_cl = 1;
    if ($#ARGV > -1 && $ARGV[0] eq "--remove-cl") {
	$print_cl = 0;
	shift (@ARGV);
    }
    @cl_attrs = ();
    @cl_partnum = ();
    @cl_partwords = ();
    $cl_words = 0;
    $cl_just_opened = 0;
}

if (/^<cl (.*)>/) {
    $depth = $#cl_attrs + 1;
    push (@cl_attrs, "$1 depth=\"$depth\"");
    push (@cl_partnum, 1);
    push (@cl_partwords, 0);
    if ($cl_words) {
	print "</clause>\n";
	$cl_words = 0;
    }
    print if ($print_cl);
    $cl_just_opened = 1;
} elsif (/^<\/cl>/) {
    pop (@cl_attrs);
    pop (@cl_partnum);
    pop (@cl_partwords);
    if ($cl_words) {
	print "</clause>\n";
	$cl_words = 0;
    }
    print if ($print_cl);
    $cl_just_opened = 0;
} else {
    if (/^[^<]/) {
	if ($#cl_partnum >= 0) {
	    if (! $cl_words) {
		if ((! $cl_just_opened) && $cl_partwords[-1]) {
		    $cl_partnum[-1]++;
		}
		print "<clause $cl_attrs[-1] partnum=\"$cl_partnum[-1]\">\n";
	    }
	    $cl_words = 1;
	    $cl_partwords[-1] = 1;
	}
    }
    print;
    $cl_just_opened = 0;
}
