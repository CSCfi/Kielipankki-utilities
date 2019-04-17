#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $section_depth = 0;
my $line = 0;

while ( <> ) {
    ++$line;
    # section start
    if (/^<section[ >]/)
    {
	if ($section_depth eq 0)
	{
	    print;
	}
	$section_depth++;
    }
    elsif (/^<\/section>/)
    {
	$section_depth--;
	if ($section_depth eq 0)
	{
	    print;
	}
    }
    else
    {
	print;
    }
}
