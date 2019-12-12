#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

use FileHandle;
my $file = FileHandle->new();

foreach my $line ( <STDIN> ) {    

    if ($line =~ /^###C: FILENAME: (.*)/ )
    {
	my $filename = $1;
	$filename =~ s/\.txt/\.conllu/;
	open(my $fh, '>:encoding(UTF-8)', $filename);
	$file = $fh;
    }
    else
    {
	print $file $line;
    }

}
