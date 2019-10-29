#!/usr/bin/perl

# Convert vertical bars in msd attributes (6th field) into spaces.

use strict;
use warnings;
use open qw(:std :utf8);

foreach my $line ( <STDIN> ) {    

    if ( $line =~ /^[^<]/ ) # comments are printed as such
    {
	if ( $line =~ /^(([^\t]+\t){5})([^\t]+)(.*)$/ )
	{
	    my $before = $1;
	    my $msd = $3;
	    my $after = $4;
	    
	    if ( $msd =~ / / )
	    {
		print STDERR "ERROR: spaces in msd field: ".$msd."\n";
		exit 1;
	    }
	    $msd =~ s/\|/ /g;
	    print $before;
	    print $msd;
	    print $after;
	    print "\n";
	}
	else
	{
	    print STDERR "ERROR: line has fewer than six fields:\n".$line."\n";
	    exit 1;
	}
    }
    else
    {
	print $line;
    }

}
