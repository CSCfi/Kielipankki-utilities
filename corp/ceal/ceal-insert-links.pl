#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $author = $ARGV[0];
my $paragraph_number = 0;

foreach my $line ( <STDIN> ) {    

    if ($line =~ /^<paragraph[> ]/)
    {
	$paragraph_number++;
	my $link_id = "";
	if ($author eq "--austen")
	{
	    $link_id = "austen_";
	}
	elsif ($author eq "--dickens")
	{
	    $link_id = "dickens_";
	}
	elsif ($author eq "--james")
	{
	    $link_id = "james_";
	}
	$link_id = $link_id.$paragraph_number;
	$line = '<link id="'.$link_id.'">'."\n".$line;
    }
    elsif ($line =~ /^<\/paragraph>/)
    {
	$line = $line.'</link>'."\n";
    }
    print $line;

}
