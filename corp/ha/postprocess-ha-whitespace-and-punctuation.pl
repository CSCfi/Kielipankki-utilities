#!/usr/bin/perl

# Postprocess result from fsm2vrt.py to handle whitespace and punctuation characters.
# Read from standard input and write to standard output.

# After: run postprocess-ha-add-lemmas.pl to add lemmas.

use strict;
use warnings;
use open qw(:std :utf8);

foreach my $line ( <STDIN> ) {

    $line =~ s/ +/ /g;    # allow only single spaces
    $line =~ s/ \t/\t/g;  # no spaces before tabs
    $line =~ s/\t /\t/g;  # no spaces after tabs
    $line =~ s/\t$//g;  # no tabs before end of line

    # Spaces on non-tag lines must be encoded as non-break spaces (U+00A0)
    unless ( $line =~ /^</ )
    {
	$line =~ s/ /\xA0/g;
    }
    
    # These must be analyzed as punctuation marks.
    my @puncts = (',', ':', ';', '!', '?', '"');

    # Process them three times (works for cases like "M.?",)
    for (my $i = 0; $i < 3; $i = $i + 1)
    {
	foreach (@puncts)
	{
	    $line =~ s/^([^<\t]+)\Q$_\E\t(.+)\n/$1\t$2\n$_\t$_\t$_\tpunct\n/g;
	    # dot is a separate case
	    $line =~ s/^([^<\t][^\t][^\t]+)\.\t(.+)\n/$1\t$2\n\.\t\.\t\.\tpunct\n/g; # foo.
	    $line =~ s/^("[^A-Z\t]+)\.\t(.+)\n/$1\t$2\n\.\t\.\t\.\tpunct\n/g;        # "f.
	    $line =~ s/^([^<"\t][^\t]+)\.\t(.+)\n/$1\t$2\n\.\t\.\t\.\tpunct\n/g;     # fo.
	    $line =~ s/^([^<A-Z\t])\.\t(.+)\n/$1\t$2\n\.\t\.\t\.\tpunct\n/g;         # f.
	}
    }

    $line =~ s/^"([^\t])/"\t"\t"\tpunct\n$1/g;  # quote at the beginning of word is punct

    print $line

}
