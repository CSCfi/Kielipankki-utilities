#!/usr/bin/perl

# Check that all text data is inside a <paragraph> and that there
# are no paragraphs inside another paragraph. Handle optional paragraphs
# (<?paragraph>); insert them where they are needed. Also add missing
# paragraphs and give a warning.

use strict;
use warnings;
use open qw(:std :utf8);

my $paragraph = 0;
my $possible_paragraph = 0;
my $paragraph_inserted = 0;
my $line = 0;

while ( <> ) {
    ++$line;
    # possible paragraph
    if (/^<\?paragraph/)
    {
	if ($paragraph ne 0) { next; }
	else { s/^<\?paragraph/<paragraph/; ++$paragraph; $possible_paragraph = 1; }
    }
    # possible paragraph end
    elsif (/^<\/\?paragraph/)
    {
	if ($possible_paragraph ne 1) { next; }
	else { s/^<\/\?paragraph/<\/paragraph/; $paragraph = 0; $possible_paragraph = 0; }
    }
    elsif (/^<paragraph/)
    {
	if ($paragraph_inserted eq 1)
	{
	    print "</paragraph>\n";
	    $paragraph_inserted = 0;
	}
	if(++$paragraph > 1)
	{
	    print STDERR join('','ERROR: paragraph inside paragraph on line ',$line,"\n");
	    exit 1;
	}
    }
    elsif (/^<\/paragraph/) { $paragraph = 0; }
    # other tags (<> is sentence boundary that must be inside paragraph)
    elsif (/^<[^>]/)
    {
	if ($paragraph_inserted eq 1)
	{
	    print "</paragraph>\n";
	    $paragraph_inserted = 0;
	}
    }
    elsif ($paragraph eq 0) # content that should be inside paragraph
    {
	unless ($paragraph_inserted eq 1)
	{
	    print STDERR join('',"warning: content not inside paragraph: ",$_,"inserting <paragraph type=\"unknown\"> ... </paragraph>\n");
	    print "<paragraph type=\"unknown\">\n";
	    $paragraph_inserted = 1;
	}
    }
    print;
}
