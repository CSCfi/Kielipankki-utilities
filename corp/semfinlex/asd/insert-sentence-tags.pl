#!/usr/bin/perl

# Divide input into sentences.

use strict;
use warnings;
use open qw(:std :utf8);

my $sentence_number = 0; # number of sentence
my $sentence = ""; # the current sentence
my $previous_sentence = "";
my $words = 0; # number of words in a sentence, including punctuation
my $words_in_total = 0;
my $limit = 100000; # limit of sentence length, print warning if exceeded

my $print_wps = "false"; # print words per sentence on average at the end

# interpret the following symbols as sentence separators if the respective threshold is exceeded:
# my $comma_threshold = 100000; # comma
# my $threshold = 100000; # hyphen, hyphen-minus, n dash, m dash and horizontal bar

my $filename = ""; # for more informative warning messages

foreach (@ARGV)
{
    if ( $_ eq "--limit" ) { $limit = -1; }
    # elsif ( $_ eq "--comma-threshold" ) { $comma_threshold = -1; }
    # elsif ( $_ eq "--threshold" ) { $threshold = -1; }
    elsif ( $_ eq "--filename" ) { $filename = "next..."; }
    elsif ( $_ eq "--print-wps") { $print_wps = "true"; }
    elsif ( $_ eq "--help" || $_ eq "-h" ) { print "Usage: $0 [--limit LIMIT] [--filename FILENAME] [--print-wps]\n"; exit 0; }
    # TODO [--comma-threshold CT] [--threshold T]
    elsif ( $limit == -1 ) { $limit = $_; }
    # elsif ( $comma_threshold == -1 ) { $comma_threshold = $_; }
    # elsif ( $threshold == -1 ) { $threshold = $_; }
    elsif ( $filename eq "next..." ) { $filename = $_; }
    else { print join("","Error: argument ",$_," not recognized\n"); exit 1; }
}

foreach my $line ( <STDIN> ) {

    # skip xml (including sentence boundary marker <>)
    if ( $sentence eq "" && $line =~ /^</ )
    {
	unless ($line =~ /^<>$/) { print $line; }
    }
    # end of sentence
    # TODO: ( $words > $comma_threshold && $line =~ /^,$/ ) || ($words > $threshold && $line =~ /^(\-|\x{002D}|\x{2013}|\x{2014}|\x{2015})$/ ) )
    # .. and ... are used for missing text or in tables; interpret them as sentence boundaries if not in the beginning of a sentence
    elsif ( $line =~ /^\.$/ || $line =~ /^\.\)$/ || $line =~ /^\.\]$/ || $line =~ /^\;$/ || $line =~ /^\:$/ || ($sentence ne "" && $line =~ /^\.\.\.?$/) || $line =~ /^</)
    {
	if ($sentence eq "")
	{
	    $line =~ s/\n$//;
	    print STDERR join('',"warning: sentence starts with '",$line,"' in file ",$filename,"', skipping the symbol\n");
	    print STDERR join('',"(previous sentence is:\n",$previous_sentence);
	    next;
	}
	if ( $line =~ /^</) # xml (including sentence boundary marker <>) -> no words
	{
	    $sentence .= "</sentence>\n";
	    unless ($line =~ /^<>$/) { $sentence .= $line; } # print xml (excluding <>) after </sentence>
	}
	elsif ( $line =~ /^\.\)$/ ) # .) -> two words
	{
	    $sentence .= ".\n)\n";
	    $words++; $words++;
	    $sentence .= "</sentence>\n";
	}
	elsif ( $line =~ /^\.\]$/ ) # .] -> two words
	{
	    $sentence .= ".\n]\n";
	    $words++; $words++;
	    $sentence .= "</sentence>\n";
	}
	else # one word
	{
	    $sentence .= $line;
	    $words++;
	    $sentence .= "</sentence>\n";
	}

	if ( $words > $limit ) { print STDERR join("","warning: sentence length is ",$words," words in sentence number ",$sentence_number," in file ",$filename,"\n"); }
	print $sentence;
	$previous_sentence = $sentence;
	$sentence = "";
	$words_in_total = $words_in_total + $words;
	$words = 0;
    }
    else
    {
	$words++;
	if ($sentence eq "")
	{
	    $sentence = join('','<sentence n="',++$sentence_number,'">',"\n");
	}
	$sentence .= $line;
    }
}


if ($sentence ne "")
{
    print STDERR join('',"Error: last sentence in file ",$filename," could not be ended:\n",$sentence);
    exit 1;
    #$sentence .= '</sentence>';
    #if ( $words > $limit ) { print STDERR join("","warning: sentence length is ",$words," words in sentence number ",$sentence_number," in file ",$filename,"\n"); }
    #$sentence .= "\n";
    #print $sentence;
}
else
{
    # sentence might contain the last xml markup that has not yet been printed
    #print $sentence;
}

# words per sentence on average
if ($print_wps eq "true")
{
    unless ($sentence_number eq 0)
    {
	my $wps = $words_in_total / $sentence_number;
	print STDERR join('',"words per sentence on average: ",$wps,"\n");
    }
    else
    {
	print STDERR join('',"words per sentence on average: (no sentences)\n");
    }
}
