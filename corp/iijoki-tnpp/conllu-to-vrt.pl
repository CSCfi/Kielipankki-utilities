#!/usr/bin/perl

# Convert conllu output to vrt format. Used for preprocessing Iijoki series.
#
# cat CONLLU_FILE | ./conllu_to_vrt.pl TITLE YEAR SRC_FILENAME > VRT_FILE

use strict;
use warnings;
use open qw(:std :utf8);

# Make sure that command line arguments are encoded right
# (book titles contain characters outside ascii range).
use I18N::Langinfo qw(langinfo CODESET);
my $codeset = langinfo(CODESET);
use Encode qw(decode);
@ARGV = map { decode $codeset, $_ } @ARGV;

my $sentence_id=1;
my $first_sentence_in_paragraph="true";

# Attributes from TNPP output. They will be changed later with vrt-keep and vrt-rename for korp.
print "<!-- #vrt positional-attributes: id word lemma upos xpos feats head deprel deps misc -->\n";

print "<text filename=\"";
print $ARGV[2];
print "\" title=\"";
print $ARGV[0];
print "\" year=\"";
print $ARGV[1];
print "\" dateto=\"";
print $ARGV[1];
print "0101\" datefrom=\"";
print $ARGV[1];
print "1231\" timefrom=\"000000\" timeto=\"235959\" author=\"Kalle P\x{00E4}\x{00E4}talo\" lang=\"fi\" publisher=\"Gummerus\">\n";

foreach my $line ( <STDIN> ) {    

    if ($line =~ /^# <\/paragraph>$/)
    {
	# next sentence will be the first one in the next paragraph
	$first_sentence_in_paragraph = "true";
	$line = "<\/sentence>\n<\/paragraph>\n";
    }
    # A sentence marked by TNPP begins
    elsif ($line =~ /^# sent_id = [0-9]+$/)
    {
	if ($first_sentence_in_paragraph eq "true")
	{
	    $line = "<sentence id=\"".$sentence_id."\">\n";
	    $first_sentence_in_paragraph = "false";
	}
	else
	{
	    # previous sentence ends and new one begins
	    $line = "<\/sentence>\n<sentence id=\"".$sentence_id."\">\n";
	}
	$sentence_id++;
    }
    $line =~ s/^# [^<].*//; # get rid of comment lines produced by TNPP
    $line =~ s/^# //;       # remove "# " from comment lines added in iijoki scripts
    $line =~ s/^\n$//;      # remove empty lines
    $line =~ s/&/&amp;/g;   # escape ampersands for korp
    print $line;

}

print "<\/text>\n";
