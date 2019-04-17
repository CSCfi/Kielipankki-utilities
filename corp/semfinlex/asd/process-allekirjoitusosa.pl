#!/usr/bin/perl

# Process <<allekirjoitusosa>> into paragraphs.

use strict;
use warnings;
use open qw(:std :utf8);

my $allekirjoitusosa = "";
my $begin = 0;

while (<>) {

    if (/^<<allekirjoitusosa>>/) { $begin = 1; }
    elsif (/^<<\/allekirjoitusosa>>/) { $begin = 0; }
    elsif ($begin eq 1) { $allekirjoitusosa .= $_; }
    else { print; }
}

$allekirjoitusosa =~ s/<\/asi:Allekirjoittaja>/<>/g;
$allekirjoitusosa =~ s/<\/asi:PaivaysKooste>/<>/g;
$allekirjoitusosa =~ s/<[^>]+>\n//g;
$allekirjoitusosa =~ s/^\n//g;

print join('','<<paragraph type="ALLEKIRJOITUSOSA">>',"\n");
print $allekirjoitusosa;
print "<<\/paragraph>>\n"

