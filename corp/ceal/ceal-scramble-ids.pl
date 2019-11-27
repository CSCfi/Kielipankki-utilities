#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $element = $ARGV[0];
my $filename = $ARGV[1];

open(my $fh, '<:encoding(UTF-8)', $filename);

foreach my $line ( <STDIN> ) {    

    if (($element eq "--paragraph" && $line =~ /^<paragraph id="[^"]+"/) ||
	($element eq "--sentence" && $line =~ /^<sentence id="[^"]+"/) ||
	($element eq "--link" && $line =~ /^<link id="[^"]+"/))
    {
	my $id = <$fh>;
	chomp $id;
	$line =~ s/id="[^"]+"/id="${id}"/;
    }
    print $line;

}

close($fh);
