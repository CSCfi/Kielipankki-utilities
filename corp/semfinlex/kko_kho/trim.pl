#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $skip = 0;

foreach my $line ( <STDIN> ) {

    # skip SKIP
    if ($skip eq 1)
    {
	if ($line =~ /<\/SKIP>/) { $skip = 0; }
	next;
    }
    if ( $line =~ /<SKIP[^>]*>/ )
    {
	$skip = 1;
	next;
    }

    # Replace <br/> with space
    $line =~ s/<br\/>/ /g;
    
    # Get rid of extra whitespace
    $line =~ s/\t//g;
    $line =~ s/ +/ /g;
    $line =~ s/^ //g;
    $line =~ s/ $//g;
    
    print $line;

}
