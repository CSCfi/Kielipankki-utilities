#!/usr/bin/perl

# Separate each xml tag on its own line.

use strict;
use warnings;
use open qw(:std :utf8);

foreach my $line ( <STDIN> ) {    

    $line =~ s/>/>\n/g; 
    $line =~ s/</\n</g;
    print $line;
}
