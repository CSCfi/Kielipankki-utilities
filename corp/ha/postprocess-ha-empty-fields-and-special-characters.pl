#!/usr/bin/perl

# Postprocess result from fsm2vrt.py and postprocess-ha-whitespace-and-punctuation.pl to handle lemmas.
# Read from standard input and write to standard output.

use strict;
use warnings;
use open qw(:std :utf8);

foreach my $line ( <STDIN> ) {

    $line =~ s/\t$/\t*/g;
    $line =~ s/\t\t/\t*\t/g;
    $line =~ s/\t\t/\t*\t/g;
    unless ($line =~ m/^</)
    {
	$line =~ s/\&/\&amp\;/g;
	$line =~ s/'/\&apos\;/g;
    }
    print $line;
}
