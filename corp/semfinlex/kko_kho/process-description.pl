#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $description_part = "";
my $other_parts = "";
my $keywords = "|"; # "|keyword1|keyword2|keyword3|"
my $in_description = 0;
my $in_keywords = 0; # always inside description

while (<>) {

    if (/^<<description>>/) { $in_description = 1; }
    elsif (/^<<\/description>>/) { $in_description = 0; }
    elsif ($in_description eq 1)
    { 
	$description_part .= $_;
	if (/^[^<]/)
	{
	    $description_part .= "<>\n"; # sentence boundary
	}
	if (/<span>|<strong>/) { $in_keywords = 1; }
	elsif (/<\/span>|<\/strong>/) { $in_keywords = 0; }
	elsif ($in_keywords eq 1)
	{
	    my $keyword = $_;
	    $keyword =~ s/|"//g; # get rid of | and "
	    $keyword =~ s/\n/|/;
	    $keywords .= $keyword;
	}
    }
    else { $other_parts .= $_; }
}

unless ($keywords eq "|")
{
    print join('','<<keywords="',$keywords,'">>',"\n");
}
print join('','<<section type="description">>',"\n");
print $description_part;
print "<</section>>\n";
print $other_parts;
