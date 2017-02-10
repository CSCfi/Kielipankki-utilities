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
count, word count difference (new - old)."

optspecs=

. $scriptdir/korp-lib.sh


vrt_count_words () {
    local corp
    corp=$1
    perl -ne '
        BEGIN {
            @attrlist = qw(corpus fn wc_new year datefrom from to srg arg
                           largeregion lcinf lclet wc wc_diff);
            if ('"$headings"') {
                print join ("\t", @attrlist) . "\n";
            }
        }
        chomp;
        if (/^<text/) {
            $wc = 0;
            %attrs = /([[:alnum:]]+?)="(.*?)"/g;
        } elsif (/^<\/text>/) {
            %attrs = (
                %attrs,
                corpus => "'"$corp"'",
                wc_new => $wc,
                wc_diff => $wc - $attrs{wc}
            );
            print join ("\t", map ("$attrs{$_}", @attrlist)) . "\n";
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
    headings=0
}

corpora=$(list_corpora scots_* | grep -v 1550)
headings=1

for corp in $corpora; do
    corpus_count_words $corp
done
