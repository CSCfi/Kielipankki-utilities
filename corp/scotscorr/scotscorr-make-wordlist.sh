#! /bin/sh
# -*- coding: utf-8 -*-

# Make a sorted and grouped word list of ScotsCorr as JSON (to be used
# in the Korp word list pop-up) from a TSV file containing tokens and
# their frequencies. Alternatively, if corpus ids are specified as
# arguments, read the token frequencies from the named corpora. The
# corpus ids may contain shell wildcards.
#
# Usage: scotscorr-make-wordlist.sh < tokenfreqs.tsv > wordlist.json
#        scotscorr-make-wordlist.sh [--output-tsv tokenfreqs.tsv]
#                                   corpus ... > wordlist.json


progname=`basename $0`
progdir=`dirname $0`

scriptdir=$progdir/../../scripts

usage_header="Usage: $progname < tokenfreqs.tsv > wordlist.json
       $progname [--output-tsv tokenfreqs.tsv]
           corpus ... > wordlist.json

Make a sorted and grouped word list of ScotsCorr as JSON (to be used
in the Korp word list pop-up) from a TSV file containing tokens and
their frequencies. Alternatively, if corpus ids are specified as
arguments, read the token frequencies from the named corpora. The
corpus ids may contain shell wildcards."

optspecs='
output-tsv=TSV_FILE
    write the tokens and their frequencies extracted from the corpora
    specified as arguments to the TSV file TSV_FILE
'

. $scriptdir/korp-lib.sh

# Process options
eval "$optinfo_opt_handler"


tee=cat
if [ "x$output_tsv" != x ]; then
    tee="tee $output_tsv"
fi

if [ "x$1" != x ]; then
    for corpus in $(list_corpora "$@"); do
	cwb-lexdecode -f $corpus
    done |
    perl -pe 's/^\s*(\d+)\s+(.*)/$2\t$1/' |
    LC_ALL=C sort |
    $scriptdir/vrt-convert-chars.py --decode |
    sed -e 's/&lt;/</g; s/&gt;/>/g; s/&amp;/\&/g' |
    perl -ne '
        chomp;
        ($w, $f) = split (/\t/);
        if ($w ne $prev) {
            if (defined ($prev)) {
                print "$prev\t$sum\n";
                $sum = 0;
            }
	    $prev = $w;
	}
	$sum += $f;
	END {
	    print "$prev\t$sum\n";
	}' |
    $tee
else
    cat
fi |
perl -CSD -ne '
    BEGIN {
        use feature "unicode_strings";
        use utf8;
    }
    chomp;
    ($w, $f) = /(.*?)\t(.*)/;
    $k = lc($w);
    $k =~ s/[^a-zA-Z0-9£’'"'"']//g;
    if ((($k eq "" || $k !~ /[[:alnum:]]/) && $w !~ /^\{.*\}$/)
        || $k =~ /^\xa3/) {
        $k = "\x06$w";
        $g = "Punctuation marks";
    } elsif ($w =~ /^\?/) {
        ($qm) = ($w =~ /^(\?+)/);
        $k = "\x02" . chr (length ($qm)) . $w;
        $g = "Words with uncertain beginning";
    } elsif ($w =~ /^\{/) {
        if ($w =~ /^\{</) {
            $k = "\x04$w";
            $g = "Word-related comments";
        } else {
            $k = "\x03$w";
            $g = "Independent comments";
        }
    } else {
	if (length ($k) != length ($w)) {
	    $k = substr ($k, 0, 1) . "$k\x02";
	} else {
	    $k = substr ($k, 0, 1) . "$k\x01";
	}
        if ($k =~ /^[0-9]/) {
            $k = "\x05$k";
            $g = "Numerals";
        } else {
            $k = "\x01$k";
	    ($g) = ($k =~ /([[:print:]])/);
	    $g = uc($g);
        }
    }
    print "$g\t$w\t$k\t$f\n"
' |
LC_ALL=C sort -t"$tab" -k3,3f -k2,2 |
grep -v '^Word-related' |
cut -d"$tab" -f1,2,4 |
sed -e 's/\\/\\\\/g; s/"/\\"/g' |
perl -ne '
    BEGIN {
        print "[\n";
        $prevg = "";
    }
    chomp;
    ($g, $w, $f) = split (/\t/);
    if ($g ne $prevg) {
        if ($prevg) {
            print "\n]],\n";
        }
        print "[\"$g\",[\n";
    } else {
        print ",\n";
    }
    $prevg = $g;
    print " [\"$w\",$f]";
    END {
        print "\n]]\n]\n";
    }
'
