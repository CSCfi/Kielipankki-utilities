#!/usr/bin/perl

# Postprocess result from fsm2vrt.py and postprocess-ha-whitespace-and-punctuation.pl to handle lemmas.
# Read from standard input and write to standard output.

use strict;
use warnings;
use open qw(:std :utf8);

foreach my $line ( <STDIN> ) {

    # Proper nouns keep their capitalization
    if ( $line =~ /\tpropn *$/ )
    {
	$line =~ s/^([^\t]+)(\t[^\t]+\t[^\t]+\tpropn)/$1\t$1$2/g;
    }
    # as do words with unrecognized POS
    elsif ( $line =~ /\t\*\*\* *$/ )
    {
	$line =~ s/^([^\t]+)(\t[^\t]+\t[^\t]+\t\*\*\*)/$1\t$1$2/g;
    }
    # and words such as "R." and "L." with no analysis.
    elsif ( $line =~ /^[A-Z]\.[\t ]+$/ )
    {
	$line =~ s/^(..)[\t ]+/$1\t$1\t*\t*\t*/g;
    }
    else
    {
	$line =~ s/^([^\t<]+)((\t[^\t]+\t[^\t]+\t[^\t])?)/$1\t\l$1$2/g;
    }

    print $line

}
