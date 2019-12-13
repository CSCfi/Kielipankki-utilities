#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $word_number = 0;
my $sentence_number = 0;

foreach my $line ( <STDIN> ) {    

    if ($line =~ /^<sentence /)
    {
	$word_number=0;
	$line = '<sentence id="'.++$sentence_number.'">'."\n";
    }
    unless ($line =~ /^</)
    {
	chomp($line);
	$line = $line."\t".++$word_number."\n";
    }
    print $line;
}
