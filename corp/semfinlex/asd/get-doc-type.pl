#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

while (<>) {
    if (/saa1:saadostyyppiNimi="([^"]+)"/)
    {
	my $doctype = $1;
	$doctype =~ s/\x{00E4}/a/g;
	$doctype =~ s/\x{00F6}/o/g;
	$doctype =~ s/\x{00C4}/A/g;
	$doctype =~ s/\x{00D6}/O/g;
	$doctype =~ s/ /_/g;
	$doctype = lc $doctype;
	print $doctype;
	print "\n";
	exit 0;
    }
}

print "(none)\n";
