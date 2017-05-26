#! /bin/sh
# -*- coding: utf-8 -*-

progname=`basename $0`
progdir=`dirname $0`

scriptdir=$progdir/../../scripts

usage_header="Usage: $progname [options] > wordcounts.tsv

Make a table of word counts (in TSV format) in each letter in the
ScotsCorr data.

The columns in the output are: corpus id, filename, word count, year,
datefrom, from, to, wgr, agr, largeregion, lcinf, lclet, old word
count, word count difference (new - old)."

optspecs='
vrt-dir=DIR
    use the VRT files in DIR instead of the encoded CWB corpus data
include-punctuation include_punct
    include punctuation marks in the word count (default: exclude)
'

. $scriptdir/korp-lib.sh


# Process options
eval "$optinfo_opt_handler"


vrt_count_words () {
    local corp
    corp=$1
    perl -CSD -e '
	use feature "unicode_strings";
	use utf8;
	@attrlist = qw(corpus period gender fn wc_new year datefrom
		       from to wgr agr largeregion lcinf lclet from_lcinf
                       wc wc_diff);
        %gender_map = (m => "male", f => "female", royal => "royal");
	if ('"$headings"') {
	    print join ("\t", @attrlist) . "\n";
	}
        while (<>) {
	    chomp;
	    if (/^<text/) {
		$wc = 0;
		%attrs = /([[:alnum:]]+?)="(.*?)"/g;
	    } elsif (/^<\/text>/) {
		$corpus = "'"$corp"'";
		($period) = ($corpus =~ /_[mf]?([\d_]+|royal)/);
		$period =~ s/_/–/;
                # Royal letters only up to 1649
                if ($period eq "royal") {
                    if ($attrs{year} < 1600) {
                        $period = "1540–1599";
                    } elsif ($attrs{year} < 1650) {
                        $period = "1600–1649";
                    }
                }
                if ($attrs{lcinf} eq "East Lothian") {
                    $attrs{lcinf} = "Lothian";
                }
		($gender) = ($corpus =~ /_(m|f|royal)/);
		$gender = $gender_map{$gender};
		%attrs = (
		    %attrs,
		    corpus => $corpus,
		    period => $period,
		    gender => $gender,
		    wc_new => $wc,
		    wc_diff => $wc - $attrs{wc},
                    from_lcinf => "$attrs{from} ($attrs{lcinf})",
		);
		print join ("\t", map ("$attrs{$_}", @attrlist)) . "\n";
	    } elsif (/^<.*>$/) {
		next;
	    } else {
		($w) = /^(.*?)(?:\t|$)/;
		if ($w =~ /^(\{.*\}|\\+)$/
                    || (! "'"$include_punct"'" && $w !~ /[[:alnum:]]/)) {
		    # print "non-word: $w\n";
		    next;
		}
	    }
	    $wc++;
        }
    '
}

cat_corpus () {
    local corp
    corp=$1
    if [ "x$vrt_dir" != x ]; then
	cat "$vrt_dir/$corp.vrt"
    else
	$scriptdir/cwbdata2vrt.py $corp |
	$scriptdir/vrt-convert-chars.py --decode
    fi
}

corpus_count_words () {
    local corp
    corp=$1
    cat_corpus $corp |
    vrt_count_words $corp
    headings=0
}

corpora=$(list_corpora scots_* | grep -v 1550)
headings=1

for corp in $corpora; do
    corpus_count_words $corp
done
