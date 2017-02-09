#! /bin/sh
# -*- coding: utf-8 -*-

progname=`basename $0`
progdir=`dirname $0`

scriptdir=$progdir/../../scripts

usage_header="Usage: $progname > wordcounts.tsv

Make a table of word counts (in TSV format) in each letter in the
ScotsCorr data.

The columns in the output are: corpus id, filename, word count, year,
datefrom, from, to, srg, arg, largeregion, lcinf, lclet, old word
count."

optspecs=

. $scriptdir/korp-lib.sh


vrt_count_words () {
    local corp
    corp=$1
    perl -ne '
        chomp;
        if (/^<text/) {
            $wc = 0;
            %attrs = /([[:alnum:]]+?)="(.*?)"/g;
        } elsif (/^<\/text>/) {
            print join ("\t",
                        "'"$corp"'", $attrs{fn}, $wc,
                        map ("$attrs{$_}",
                             qw(year datefrom from to srg arg largeregion lcinf lclet wc)),
                             $wc - $attrs{wc})
                  . "\n";
        } elsif (/^<.*>$/) {
            next;
        } else {
            ($w) = /^(.*?)\t/;
            if ($w =~ /^(\{.*\}|\\+)$/ || $w !~ /[[:alnum:]]/) {
		# print "non-word: $w\n";
		next;
            }
        }
        $wc++;
    '
}

corpus_count_words () {
    local corp
    corp=$1
    $scriptdir/cwbdata2vrt.py $corp |
    $scriptdir/vrt-convert-chars.py --decode |
    vrt_count_words $corp
}

corpora=$(list_corpora scots_* | grep -v 1550)

for corp in $corpora; do
    corpus_count_words $corp
done
