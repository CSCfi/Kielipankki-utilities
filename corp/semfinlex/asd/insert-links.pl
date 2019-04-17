#!/usr/bin/perl

# Add <link> around each <section> for parallel corpus.

use strict;
use warnings;
use open qw(:std :utf8);

my $id = "";

while (<>)
{
    if (/^<section id="([^"]*)"/)
    {
	$id = $1;
	print join('',"<link id=\"",$id,"\">\n");
	print;
    }
    elsif (/^<\/section>/)
    {
	print;
	print "</link>\n";
    }
    else
    {
	print;
    }
}
