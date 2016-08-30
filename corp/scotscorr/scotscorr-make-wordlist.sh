#! /bin/sh

# Make a sorted and grouped word list of ScotsCorr as JSON (to be used
# in the Korp word list pop-up) from a TSV file containing tokens and
# their frequencies.
#
# Usage: scotscorr-make-wordlist.sh < tokenfreqs.tsv > wordlist.json


tab='	'

grep -v '^{<' |
grep -v ">}$tab" | 
perl -ne '
    chomp;
    ($w, $f) = /(.*?)\t(.*)/;
    $k = lc($w);
    $k =~ s/[^a-zA-Z0-9]//g;
    if (! $k) {
        $k = "\x03$w";
    } elsif ($k =~ /^[0-9]/) {
        $k = "\x02$w";
    } else {
        if ($k ne $w) {
            $k .= "\x02";
        } else {
            $k .= "\x01";
        }
        $k = "\x01$k";
    }
    $g = uc(substr($k, 1, 1));
    print "$g\t$w\t$k\t$f\n"
' |
LC_ALL=C sort -t"$tab" -sf -k3,3 -k2,2 |
cut -d"$tab" -f1,2,4 |
sed -e 's/\\/\\\\/g; s/"/\\"/g' |
gawk -F"$tab" '
    BEGIN {
        print "["
    }
    {
        g = toupper(substr($1,1,1));
        if (g != prev) {
            if (prev) { print "\n]]," }
            g0 = g
            if (g == "\\") { g0 = "\\\\" }
            printf "[\"%s\",[", g0
        }
        if (g == prev) {
            print ","
        } else {
            printf "\n"
        }
        prev = g
        printf " [\"%s\",%s]", $1, $2
    }
    END {
        print "\n]]\n ]"
    }'
