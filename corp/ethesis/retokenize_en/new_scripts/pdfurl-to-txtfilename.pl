#!/usr/bin/perl

# E.g. "https://helda.helsinki.fi/bitstream/43215/94540/5/PDFNAME.pdf      2013-04" -> "en_PDFNAME.txt"

use strict;
use warnings;
use open qw(:std :utf8);

my $pdfurl="";
my $date="";

foreach my $line ( <STDIN> ) {

    if ($line =~ /^([^\t]+)/)
    {
	$pdfurl=$1;
	chomp($pdfurl);
	$pdfurl =~ s/.*\/(.*)\.pdf/$1\.txt/;
	$pdfurl =~ s/^(.)/en_$1/;
	print $pdfurl."\n";
    }
    else
    {
	exit 1;
    }

}
