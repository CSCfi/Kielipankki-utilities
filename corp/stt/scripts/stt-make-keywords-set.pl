#! /usr/bin/perl -CSD

# stt-make-keywords-set.pl
#
# Create a mapping from the keywords values of the STT corpus to
# corresponding feature-set values, with individual keywords (or
# phrases) as values of the set. Because the original keywords are
# rather inconsistently formatted, a number of heuristics are used to
# try to find out the individual keywords. The heuristics are not
# perfect, however.
#
# Usage: stt-make-keywords-set.pl keywords-all.txt > keywords-set.tsv
#
# Input: A text file with one text_keywords value on each line (each
#     value only once)
# Output: A TSV file with the original value as the first field and
#     its set-valued representation as the second field. This can be
#     used as input to cwbdata-add-structattrs.sh with text_keywords
#     as the key attribute.
#
# Author: Jyrki Niemi

# TODO:
# - Add some descriptive comments to the different substitutions: what
#   they do and why are they needed


use utf8;
use feature "unicode_strings";

use List::MoreUtils qw(uniq);

while (<>) {
    chomp;
    $orig = $_;
    s/([[:lower:]]{3})\./$1,/g;
    s/^,+//;
    s/,+$//;
    s/^/|/;
    s/$/|/;
    s/§/ /g;
    s/&gt//g;
    s/\+\s/ /g;
    s/(\p{Lu})\+/$1/g;
    # Protect "1. Divisioona" and similar to avoid breaking it
    s/([^\p{L}]\d\.)\s+(\p{Lu})/$1\x01$2/g;
    s/\s*(?:[,:;.+¨'"'"']+)\s*(\p{Lu})/|$1/g;
    # Unprotect
    s/\x01/ /g;
    s/\s*[;]\s*/|/g;
    s/(\p{Ll}|\d)\s*(\p{Lu}(?:\p{Ll}|\|))/$1|$2/g;
    s/(\p{Lu})(\p{Lu}\p{Ll})/$1|$2/g;
    s/(\S{4,})[[:punct:]¨]+(\|)/$1$2/g;
    s/,(\S)/, $1/g;
    s/[¨´]//g;
    s/÷/ö/g;
    s/(\w)#(\w)/$1$2/g;
    s/ ,/,/g;
    s/( ja [^,|]+),\s+/$1|/g;
    s/,\s+(?![^|]+\s+ja\s+)/|/g;
    s/-\.|--+/-/g;
    s/\.\.+/./g;
    s/(\d)\.-/$1-/g;
    s/(\d|v)\.(\p{Ll})/$1. $2/g;
    s/(\p{Lu})\.(\p{Ll})/$1 $2/g;
    s/\s([^0-9mv])\|/|$1|/g;
    s/\|\.\s*/|/g;
    s/(\p{Lu}{2})\s+(\p{Lu}\p{Ll})/$1|$2/g;
    s/\s*\|\s*/|/g;
    s/,\|/|/g;
    s/(\p{Ll}{2,})(\p{Lu}|[[:digit:]])/$1|$2/g;
    s/(\|)(.)/$1\U$2\E/g;
    s/^\|//;
    s/\|$//;
    @vals = grep (! /^(.|[[:punct:][:digit:]]+)$/ && ! /\/\//,
                  uniq (split (/\|/)));
    $line = ($#vals < 0 ? "|" : "|" . join ("|", @vals) . "|");
    print "$orig\t$line\n";
}
