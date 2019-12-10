#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $first_paragraph = "true";
my $first_sentence = "true";

# English text
foreach my $line ( <STDIN> ) {    

    if ($line =~ /^<paragraph>/ )
    {
	if ($first_paragraph eq "true")
	{
	    $first_paragraph = "false";
	}
	else
	{
	    print "</sentence>\n";
	    print "</paragraph>\n";
	}
	$first_sentence = "true";
    }
    elsif ($line =~ /^<sentence / )
    {
	if ($first_sentence eq "true")
	{
	    $first_sentence = "false";
	}
	else
	{
	    print "</sentence>\n";
	}
    }
    else
    {
	$line =~ s/&/&amp;/g;
	$line =~ s/>/&gt;/g;
	$line =~ s/</&lt;/g;
    }
    print $line;
}

print "</sentence>\n";
print "</paragraph>\n";


