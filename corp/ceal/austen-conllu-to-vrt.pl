#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $lang = $ARGV[0];

my $chapter = "false";
my $paragraph = "false";
my $heading_paragraph = "false";
my $sentence = "false";

my $paragraph_number = 0;
my $sentence_number = 0;

print "<!-- #vrt positional-attributes: id word lemma upos xpos feats head deprel deps misc -->\n";

# English text
if ($lang eq "--eng")
{
    print '<text filename="?" title="Pride and Prejudice" datefrom="?" dateto="?" timefrom="000000" timeto="235959"';
    print ' author="Jane Austen" lang="en" publisher="?">';
    print "\n";
}
elsif ($lang eq "--fin")
{
    print '<text filename="?" title="Ylpeys ja ennakkoluulo" year="2013" datefrom="20130101" dateto="20131231" timefrom="000000" timeto="235959"';
    print ' author="Kersti Juva" lang="fi" publisher="?">';
    print "\n";
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
