#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

use FileHandle;
my $file = FileHandle->new();
my $skip = "true";

foreach my $line ( <STDIN> ) {    

    if ($line =~ /^# FILENAME: (.*)/ )
    {
	$skip = "false";
	my $filename = $1;
	$filename =~ s/\.txt/\.conllu/;
	open(my $fh, '>:encoding(UTF-8)', $filename);
	$file = $fh;
    }
    else
    {
	unless ($skip eq "true")
	{
	    print $file $line;
	}
    }

}
