#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $before = "";
my $after = "";
my $div_depth = 0;
my $filename = ""; # for more informative warning messages

foreach (@ARGV)
{
    if ( $_ eq "--filename" ) { $filename = "next..."; }
    elsif ( $filename eq "next..." ) { $filename = $_; }
    else { print join("","Error: argument ",$_," not recognized\n"); exit 1; }
}


while (<STDIN>) {

    if (/^<div[ >]/)
    {
	$div_depth++;
	if ($div_depth eq 1) { $before = "<<part>>\n"; }
	elsif ($div_depth eq 2) { $before = "<<chapter>>\n"; }
	elsif ($div_depth eq 3) { $before = "<<section>>\n"; }
	else { print STDERR join('',"Error: <div> depth exceeds 3 in file ",$filename,".\n"); exit 1; }
    }
    elsif (/^<\/div>/)
    {
	$div_depth--;
	if ($div_depth eq 0) { $after = "<</part>>\n"; }
	elsif ($div_depth eq 1) { $after = "<</chapter>>\n"; }
	elsif ($div_depth eq 2) { $after = "<</section>>\n"; }
	else { print STDERR join('',"Error: <div> depth exceeds 3 in file ",$filename,".\n"); exit 1; }
    }
    elsif (/^<p[ >]/)
    {
	$before = "<<paragraph type=\"paragraph\">>\n";
    }
    elsif (/^<\/p>/)
    {
	$after = "<</paragraph>>\n";
    }

    print $before;
    $before = "";
    print;
    print $after;
    $after = "";
}
