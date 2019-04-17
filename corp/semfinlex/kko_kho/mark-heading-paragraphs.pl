#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

#<h2 id="19800001saloa0">
#    ASIAN KÄSITTELY ALEMMISSA OIKEUKSISSA
#    </h2>

# skip: <h2 id="19960106aloa0"/>

my $delayed = "";
my $title = "";

while (<>) {
    if (/^<h[23][ >]/)
    {
	unless (/\/>$/)
	{
	    $delayed .= "<<paragraph type=\"heading\">>\n";
	}
    }
    elsif (/^<\/h[23]>/)
    {
	$delayed .= "<</paragraph>>\n";
	$title =~ s/\n//g;
	$title =~ s/'/&apos;/g;
	$title =~ s/"/&quot;/g;
	$title =~ s/<[^>]*>//g; # e.g. <em>
	unless ($title eq "")
	{
	    print join('',"<<title=\"",$title,"\">>\n");
	}
	print $delayed;
	$delayed = "";
	$title = "";
    }
    elsif ($delayed ne "")
    {
	$delayed .= $_;
	$title .= $_;
    }
    else
    {
	print;
    }
}
