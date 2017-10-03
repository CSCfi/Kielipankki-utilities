#! /usr/bin/perl -CSD -w
# -*- coding: utf-8 -*-


# Add to the ScotsCorr VRT data a positional comment attribute to
# words having a following word-related comment: a comment of the form
# {<...}, but excluding certain comments containing a < but
# nevertheless referring to more than a single word.
#
# Usage: scotscorr-vrt-add-comments.pl < input.vrt > output.vrt


use feature "unicode_strings";
use utf8;


my $prev = "";

while (my $line = <>) {
    chomp ($line);
    if ($prev) {
	if ($prev =~ /^</) {
	    print "\n";
	} elsif ($line =~ /^\{&lt;/
		 && $line !~ /^\{&lt;(Fraser|French|Latin|hand\s[12]|in margin|italic|outdented to the left|repeated)\}/) {
	    print "\t$line\n";
	} else {
	    print "\t\n";
	}
    }
    print $line;
    $prev = $line;
}

print "\n";
