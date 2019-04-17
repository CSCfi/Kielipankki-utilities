#!/usr/bin/perl

# Skip some parts of text: <tau:table>, <te>, <ete> and <pdf>.
# Tables are difficult to parse and split into sentences.
# Also replace <br /> with space and get rid of extra whitespace.

use strict;
use warnings;
use open qw(:std :utf8);

my $table = 0;
my $te = 0;
my $ete = 0;
my $pdf = 0;

foreach my $line ( <STDIN> ) {

    # skip tables
    if ($table eq 1)
    {
	if ($line =~ /<\/tau:table>/) { $table = 0; }
	next;
    }
    if ( $line =~ /<tau:table[^>]*>/ )
    {
	$table = 1;
	next;
    }
    # skip table entries
    if ($te eq 1)
    {
	if ($line =~ /<\/te>/) { $te = 0; }
	next;
    }
    if ( $line =~ /<te>/ )
    {
	$te = 1;
	next;
    }
    # skip <ete>
    if ($ete eq 1)
    {
	if ($line =~ /<\/ete>/) { $ete = 0; }
	next;
    }
    if ( $line =~ /<ete>/ )
    {
	$ete = 1;
	next;
    }
    # skip <pdf>
    if ($pdf eq 1)
    {
	if ($line =~ /<\/pdf[^>]*>/) { $pdf = 0; }
	next;
    }
    if ( $line =~ /<pdf[^>]*>/ )
    {
	$pdf = 1;
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
