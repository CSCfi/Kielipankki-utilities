#!/usr/bin/perl

# Add <link> around each <section> for parallel corpus.

use strict;
use warnings;
use open qw(:std :utf8);

my $part = "";
my $chapter = "";
my $prefix = "";

foreach (@ARGV)
{
    if ( $_ eq "--link-prefix" ) { $prefix = "next..."; }
    elsif ( $prefix eq "next..." ) { $prefix = $_; }
    else { print join("","Error: argument ",$_," not recognized\n"); exit 1; }
}


while (<STDIN>)
{
    if (/^<part id="([^"]+)"/)
    {
	$part = $1;
    }
    elsif (/^<\/part>/)
    {
	$part = "";
    }
    elsif (/^<chapter id="([^"]+)"/)
    {
	$chapter = $1;
    }
    elsif (/^<\/chapter>/)
    {
	$chapter = "";
    }
    elsif (/^<section id="([^"]+)"/)
    {
	my $section = $1;
	my $id = "";
	unless ($prefix eq "") { $id .= join('',$prefix,"_"); }
	unless ($part eq "") { $id .= join('',"part",$part,"_"); }
	unless ($chapter eq "") { $id .= join('',"chapter",$chapter,"_"); }
	$id .= join('',"section",$section);
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
