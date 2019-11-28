#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $chapter = "false";
my $paragraph = "false";
my $heading_paragraph = "false";
my $sentence = "false";

my $paragraph_number = 0;
my $sentence_number = 0;

print "<!-- #vrt positional-attributes: id word lemma upos xpos feats head deprel deps misc -->\n";

my $lang = $ARGV[0];

# English text
if ($lang eq "--eng")
{
    print '<text filename="" title="Washington Square" year="1880" datefrom="18800101" dateto="18801231" timefrom="000000" timeto="235959" author="Henry James" lang="en">'."\n";
}
# Finnish text
elsif ($lang eq "--fin")
{
    print '<text filename="" title="Washingtonin aukio" year="2003" datefrom="20030101" dateto="20031231" timefrom="000000" timeto="235959" author="Henry James" translator="Kersti Juva" lang="fi" publisher="Otava">'."\n";
}

foreach my $line ( <STDIN> ) {    

    if ($line =~ /^<chapter /)
    {
	$chapter = "true";
    }
    elsif ($line =~ /^<\/chapter>/)
    {
	$chapter = "false";
	$paragraph = "false";
	$sentence = "false";
	print "</sentence>\n</paragraph>\n";
    }
    elsif ($line =~ /^<paragraph type="heading">/)
    {
	$heading_paragraph = "true";
	$paragraph_number++;
	$line =~ s/<paragraph type="heading">/<paragraph id="${paragraph_number}" type="heading">/;
    }
    elsif ($line =~ /^<paragraph>/)
    {
	if ($heading_paragraph eq "true")
	{
	    $heading_paragraph = "false";
	    $paragraph = "true";
	    next;
	}
	if ($paragraph eq "true")
	{
	    $sentence = "false";
	    print "</sentence>\n</paragraph>\n";
	}
	$paragraph = "true";
	$paragraph_number++;
	$line =~ s/<paragraph>/<paragraph id="${paragraph_number}">/;
    }
    elsif ($line =~ /^<sentence>/)
    {
	if ($sentence eq "true")
	{
	    print "</sentence>\n";
	}
	$sentence = "true";
	$sentence_number++;
	$line =~ s/<sentence>/<sentence id="${sentence_number}">/;
    }
    unless ($line =~ /^ *$/)
    {
	print $line;
    }
}

print "</text>\n";
