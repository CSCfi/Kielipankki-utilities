#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $first_paragraph = "true";
my $first_sentence = "true";

print "<!-- #vrt positional-attributes: id word lemma upos xpos feats head deprel deps misc -->\n";

foreach my $line ( <STDIN> ) {    

    $line =~ s/^# newpar/<paragraph>/;
    $line =~ s/^# sent_id = ([0-9]+)/<sentence id="$1">/;
    $line =~ s/^# text .*//;
    $line =~ s/^# newdoc//;
    $line =~ s/^# *//;
    $line =~ s/ +/ /g;

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
    unless ($line =~ /^</)
    {
	$line =~ s/&/&amp;/g;
	$line =~ s/>/&gt;/g;
	$line =~ s/</&lt;/g;
    }
    else
    {
	$line =~ s/'/&apos;/g;
    }
    unless ($line =~ /^\n$/)
    {
	print $line;
    }
}

print "</sentence>\n";
print "</paragraph>\n";
# Append </text> to the last <text> that will intentionally miss </text>
# as TNPP cannot have a comment line at the end of input.
print "</text>\n";
