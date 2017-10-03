#! /usr/bin/perl -CSD -w
# -*- coding: utf-8 -*-

# Fix the letter word count attribute (wc) in the ScotsCorr VRT data
# based on a TSV file with two columns: letter file name and word
# count.
#
# Usage: scotscorr-vrt-fix-wc.pl letter_wordcounts.tsv < input.vrt > output.vrt


use feature "unicode_strings";
use utf8;


$wcfile = shift (@ARGV);

%wc = ();

if (! open ($wcf, "<", $wcfile)) {
    die ("word count file $wcfile not found");
}

for my $line (<$wcf>) {
    chomp ($line);
    my ($fn, $wc) = split (/\t/, $line);
    $wc{$fn} = $wc;
}

close ($wcf);

while (<>) {
    if (/^<text.* fn="(.*?)"/) {
	my $fn = $1;
	my $wc = $wc{$fn} || "";
	if ($wc eq "") {
	    warn "No word count found for filename $fn";
	}
	$_ =~ s/ wc=".*?"/ wc="$wc"/;
    }
    print;
}
