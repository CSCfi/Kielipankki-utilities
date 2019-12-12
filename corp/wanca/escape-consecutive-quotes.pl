#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $quote="false";
my $linenum=0;
my $latest_line="";

foreach my $line ( <STDIN> ) {    

    $linenum++;
    if ($line =~ /^'\t/)
    {
	if ($quote eq "true")
	{
	    print STDERR "consecutive quotes on line ".$linenum.", escaping them as <'\n";
	    $latest_line =~ s/^'/<'/;
	    $line =~ s/^'/<'/;
	}
	$quote="true";
    }
    else
    {
	$quote="false";
    }
    print $latest_line;
    $latest_line=$line;
}
print $latest_line;
