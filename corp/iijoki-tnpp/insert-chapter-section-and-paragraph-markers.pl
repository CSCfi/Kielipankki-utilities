#!/usr/bin/perl

# Insert chapter, section and paragraph markers into a book from Iijoki series.

use strict;
use warnings;
use open qw(:std :utf8);

my $empty_lines = 0;
my $line_number = 0;
my $latest_element = "";
my $first_line = "true";
my $first_chapter_encountered = "false";
my $first_section_of_chapter = "true";
my $first_paragraph_of_section = "true";
my $notitletag = "false";
my $titletag = "false";

foreach my $line ( <STDIN> ) {    

    $line_number++;
    $line =~ s/\x{000D}\x{000A}/\x{000A}/; # convert CR LF newlines into LF

    # Whether the text is explicitly marked as being a title or not being a title
    if ($line =~ /^<notitle>$/)
    {
	$notitletag = "true";
	next;
    }
    elsif ($line =~ /^<\/notitle>$/)
    {
	$notitletag = "false";
	next;
    }
    elsif ($line =~ /^<title>$/)
    {
	$titletag = "true";
	next;
    }
    elsif ($line =~ /^<\/title>$/)
    {
	$titletag = "false";
	next;
    }

    # Text before first chapter, containing author, previous works, publisher etc.
    # This is marked as one paragraph that is not inside a chapter or section.
    if ($first_line eq "true")
    {
	$line = "###C: <paragraph>\n".$line;
	$first_line = "false";
    }

    # Chapters from 1-19 and "I" and "II"
    # ("I" and "II" are used only in the last book)
    elsif ($line =~ /^(((ENSIMM\x{00C4}INEN|TOINEN|((KOLMAS|NELJ\x{00C4}S|VIIDES|KUUDES|SEITSEM\x{00C4}S|KAHDEKSAS|YHDEKS\x{00C4}S)(TOISTA)?)|KYMMENES|YHDESTOISTA|KAHDESTOISTA) LUKU)|(II?))$/)
    {
	if ($first_chapter_encountered eq "false")
	{
	    $line = "###C: <\/paragraph>\n###C: <chapter title=\"".$1."\">\n###C: <paragraph type=\"heading\">\n".$line."###C: <\/paragraph>\n";
	    $first_chapter_encountered = "true";
	}
	else
	{
	    $line = "###C: <\/paragraph>\n###C: <\/section>\n###C: <\/chapter>\n###C: <chapter title=\"".$1."\">\n###C: <paragraph type=\"heading\">\n".$line."###C: <\/paragraph>\n";
	}
	$empty_lines=0;
	$latest_element="<chapter>";
	$first_section_of_chapter = "true";
	# Print titles so that they can be manually checked
	print STDERR "chapter title: \"".$1."\"\n";
    }
    # Sections inside chapters
    elsif ($first_chapter_encountered eq "true" && $notitletag eq "false" && $empty_lines > 1 && $line =~ /^([^a-z\n]+( [^a-z])*)$/)
    {
	my $title = $1;
	my $issue_warning = "false";
	# Consecutive section titles
	if ($latest_element eq "<section>")
	{
	    $issue_warning = "true";
	}
	# Section title consisting of one cardinal number
	if ($line =~ /^[1-9]([0-9])?$/)
	{
	    ;
	}
	# Spurious-looking section title
	elsif ($line =~ /[A-Z\x{00C4}\x{00D6}] [A-Z\x{00C4}\x{00D6}] [A-Z\x{00C4}\x{00D6}] / || $line !~ /[A-Z\x{00C4}\x{00D6}]/)
	{
	    if ($titletag eq "false")
	    {
		$issue_warning = "true";
	    }
	}
	# All other titles are ok

	if ($issue_warning eq "true")
	{
	    print STDERR "----- warning: spurious title (on line ".$line_number.")\n";
	}

	if ($first_section_of_chapter eq "true")
	{
	    $line = "###C: <section title=\"".$title."\">\n###C: <paragraph type=\"heading\">\n".$line."###C: <\/paragraph>\n";
	    $first_section_of_chapter = "false";
	}
	else
	{
	    $line = "###C: <\/paragraph>\n###C: <\/section>\n###C: <section title=\"".$title."\">\n###C: <paragraph type=\"heading\">\n".$line."###C: <\/paragraph>\n";
	}

	$empty_lines=0;
	$latest_element="<section>";
	$first_paragraph_of_section = "true";
	# Print titles so that they can be manually checked
	print STDERR "  section title: \"".$title."\"\n";
    }
    elsif ($first_chapter_encountered eq "true" && $line =~ /^ *$/)
    {
	$empty_lines++;
    }
    elsif ($first_chapter_encountered eq "true")
    {
	if ($first_paragraph_of_section eq "true")
	{
	    $line = "###C: <paragraph>\n".$line;
	    $first_paragraph_of_section = "false";
	}
	else
	{
	    $line = "###C: <\/paragraph>\n###C: <paragraph>\n".$line;
	}
	$latest_element = "<paragraph>";
	$empty_lines = 0;
    }
    
    print $line;
}

# TNPP does not allow input that ends in a comment. The analysis of the last line is later removed.
print "###C: <\/paragraph>\n###C: <\/section>\n###C: <\/chapter>\nTNPP_INPUT_CANNOT_END_IN_COMMENT_LINE\n";
