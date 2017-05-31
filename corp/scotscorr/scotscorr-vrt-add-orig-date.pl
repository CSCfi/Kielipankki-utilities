#! /usr/bin/perl -CSD -w
# -*- coding: utf-8 -*-


# Add to ScotsCorr VRT data the "original" date (as written in the
# letter files) as the "date" attribute of text elements, based on the
# letter file name. The dates are read from the TSV file
# letter_date.tsv with two columns: letter file name and date.
#
# Usage: scotscorr-vrt-add-orig-date letter_date.tsv < input.vrt > output.vrt


use feature "unicode_strings";
use utf8;


$datefile = shift (@ARGV);

%date = ();

if (! open ($df, "<", $datefile)) {
    die ("Date file $datefile not found");
}

for my $line (<$df>) {
    chomp ($line);
    my ($fn, $date) = split (/\t/, $line);
    $date{$fn} = $date;
}

close ($df);

while (<>) {
    if (/^<text.* fn="(.*?)"/) {
	my $fn = $1;
	my $date = $date{$fn} || "";
	if ($date eq "") {
	    warn "No date found for filename $fn";
	}
	$_ =~ s/>\n/ date="$date">\n/;
    }
    print;
}
