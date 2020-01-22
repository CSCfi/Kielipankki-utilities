#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

use FileHandle;
my $file = FileHandle->new();
my $skip_beginning = "true"; # skip beginning of file
my $skip_filename = "false"; # skip filename lines

foreach my $line ( <STDIN> ) {    

    if ($line =~ /^# FILENAME: (.*)/ )
    {
	$skip_beginning = "false";
	$skip_filename = "true";
	my $filename = $1;
	$filename =~ s/\.txt/\.conllu/;
	open(my $fh, '>:encoding(UTF-8)', $filename);
	$file = $fh;
    }
    elsif ($line =~ /^$/)
    {
	$skip_filename = "false";
    }
    else
    {
	unless ($skip_beginning eq "true" || $skip_filename eq "true")
	{
	    print $file $line;
	}
    }

}
