#!/usr/bin/perl

# Add <link> around each <section> for parallel corpus.
# Also, replace section id with link id.

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
	print;
    }
    elsif (/^<\/part>/)
    {
	$part = "";
	print;
    }
    elsif (/^<chapter id="([^"]+)"/)
    {
	$chapter = $1;
	print;
    }
    elsif (/^<\/chapter>/)
    {
	$chapter = "";
	print;
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
	# Use link id also for section
	my $line = $_;
	$line =~ s/id="[^"]+"/id="${id}"/;
	print $line;
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
