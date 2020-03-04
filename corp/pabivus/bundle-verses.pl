#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

if ( $ARGV[0] eq "--help" || $ARGV[0] eq "-h" )
{
    print "bundle-verses.pl FROM TO REPLACE\n";
    print "Bundle verses from FROM to TO and replace the id with REPLACE\n";
    print "Input comes from standard input, output is written to standard output\n";
    print "E.g. bundle-verses.pl MRK.11.29 MRK.11.30 MRK.11.29-30\n";
    print "Alternative: bundle-verses.pl REPLACE (FROM and TO are inferred from REPLACE)\n";
    exit(0);
}

my $replace = "";
my $from = "";
my $to = "";

if (scalar @ARGV eq 1)
{
    if ( $ARGV[0] =~ /(...\.[0-9]+\.)([0-9]+)\-([0-9]+)/)
    {
	$from = $1.$2;
	$to = $1.$3;
	$replace = $ARGV[0];
    }
}
elsif (scalar @ARGV eq 3)
{
    $from = $ARGV[0];
    $to = $ARGV[1];
    $replace = $ARGV[2];
}
else
{
    print STDERR "Error: wrong number of arguments\n";
    exit(1);
}

my $bundling = "false";
my $bundling_done = "false";

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
	    if ( $bundling eq "false" )
	    {
		print STDERR "Warning: end verse ".$to." encountered but no begin verse ".$from."\n";
	    }
	    else
	    {
		$line = ""; # remove link start tag
		$bundling = "false";
		$bundling_done = "true";
	    }
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

if ( $bundling eq "true" )
{
    print STDERR "Error: no end verse ".$to." encountered\n";
    exit(1);
}
elsif ( $bundling_done eq "false" )
{
    print STDERR "Warning: no bundling done for ".$replace."\n";
}
