#! /bin/sh
# -*- coding: utf-8 -*-

# Make a sorted and grouped word list of ScotsCorr as JSON (to be used
# in the Korp word list pop-up) from a TSV file containing tokens and
# their frequencies.
#
# Usage: scotscorr-make-wordlist.sh < tokenfreqs.tsv > wordlist.json


tab='	'

# grep -v '^{<' |
# grep -v ">}$tab" |
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
