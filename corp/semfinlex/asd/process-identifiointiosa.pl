#!/usr/bin/perl

# Divide <<identifiointiosa>> into paragraphs.

use strict;
use warnings;
use open qw(:std :utf8);

my $identifiointiosa = "";
my $begin = 0;
my $delayed = "";

while (<>) {

    if (/^<<identifiointiosa>>/) { $begin = 1; }
    elsif (/^<<\/identifiointiosa>>/) { $begin = 0; }
    elsif ($begin eq 1) { $identifiointiosa .= $_; }
    else { $delayed .= $_; }
}

my $viitteet = "";

if ($identifiointiosa =~ /<met:AsiakirjaViitteet>((.|\n)*)<\/met:AsiakirjaViitteet>/)
{
    $viitteet = $1;
    $viitteet =~ s/<\/sis1:ViiteTeksti>/<>/g;
    $viitteet =~ s/<[^>]+>\n//g;
    $viitteet =~ s/^\n//g;
    $identifiointiosa =~ s/<met:AsiakirjaViitteet>(.|\n)*//g;
}

$identifiointiosa =~ s/<[^>]+>\n//g;
$identifiointiosa =~ s/^\n//g;

print join('','<<paragraph type="IDENTIFIOINTIOSA">>',"\n");
print $identifiointiosa;
print "<</paragraph>>\n";
unless ($viitteet eq "")
{
print join('','<<paragraph type="VIITTEET">>',"\n");
print $viitteet;
print "<</paragraph>>\n";
}
print $delayed;
