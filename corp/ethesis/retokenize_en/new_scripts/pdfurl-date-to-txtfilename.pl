#!/usr/bin/perl

# e.g. "https://helda.helsinki.fi/bitstream/2457625/192345/5/PDFNAME.pdf 2010-05" -> "[en|eng||*]_P_2010-05DFNAME.txt"
# where [en|eng||*] is defined in first command line parameter

use strict;
use warnings;
use open qw(:std :utf8);

my $pdfurl="";
my $date="";
my $lang=$ARGV[0];

foreach my $line ( <STDIN> ) {

    if ($line =~ /^([^\t]+)/)
    {
	$pdfurl=$1;
	chomp($pdfurl);
	if ($line =~ /^([^\t]+)\t([^\t]+)$/)
	{
	    $date=$2;
	    chomp($date);
	    $date =~ s/\://g;
	}
	else
	{
	    $date="";
	}
	$pdfurl =~ s/.*\/(.*)\.pdf/$1\.txt/;
	$pdfurl =~ s/^(.)/${lang}_$1_${date}/;
	print $pdfurl."\n";
    }
    else
    {
	exit 1;
    }

}
