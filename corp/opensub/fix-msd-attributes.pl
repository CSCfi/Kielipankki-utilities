#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

while (<STDIN>)
{
    unless (/^</)
    {
	# Replace "|" with " " in morphological analyses (now 5th and 10th fields)
	if (/^([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t)([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t)(.*)$/)
	{
	    my $first=$1;
	    my $msd1=$2;
	    my $middle=$3;
	    my $msd2=$4;
	    my $last=$5;
	    $msd1 =~ s/\|/ /g;
	    $msd2 =~ s/\|/ /g;
	    $_ = $first.$msd1.$middle.$msd2.$last."\n";
	}
    }
    print;
}
