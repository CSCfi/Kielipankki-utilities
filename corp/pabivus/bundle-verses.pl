#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

if ( $ARGV[0] eq "--help" || $ARGV[0] eq "-h" )
{
    print "bundle-verses.sh FROM TO REPLACE\n";
    print "Bundle verses from FROM to TO and replace the id with REPLACE\n";
    print "Input comes from standard input, output is written to standard output\n";
    print "E.g. bundle-verses.pl MRK.11.29 MRK.11.30 MRK.11.29-30\n";
    exit(0);
}

my $from = $ARGV[0];
my $to = $ARGV[1];
my $replace = $ARGV[2];

my $bundling = "false";

foreach my $line ( <STDIN> )
{
    if ($line =~ /^<link id="([^"]*)"/)
    {
	if ( $1 eq $from )
	{
	    $bundling = "true";
	    $line =~ s/ id="[^"]*"/ id="${replace}"/; # replace link start tag id with REPLACE
	}
	elsif ( $1 eq $to )
	{
	    $line = ""; # remove link start tag
	    $bundling = "false";
	}
	elsif ( $bundling eq "true" )
	{
	    $line = ""; # remove link start tag
	}
    }
    elsif ($line =~ /^<\/link>/ && $bundling eq "true")
    {
	$line = ""; # remove link end tag
    }
    print $line;
}
