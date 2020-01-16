#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $number=0;

# English text
foreach my $line ( <STDIN> ) {    

    if ($line =~ /^<sentence / )
    {
	$number++;
	$line =~ s/id="[0-9]+"/id="${number}"/;
    }
    print $line;

}
