#! /bin/bash

# Fix and augment the ScotsCorr VRT data by running several auxiliary
# scripts
#
# Usage: scotscorr-vrt-fix-all.sh
#
# The script uses fixed input and output directories. It produces an
# output file for each input file (subcorpus VRT).
#
# If the data is updated, you should first run this script, then
# scotscorr-count-words.sh on the fixed files to generate $wcfile, and
# finally rerun this script.

# Bash needed because of process substitution


scriptdir=$(dirname $0)

basedir=/v/corpora/src/scotscorr
inputdir=$basedir/vrt
outputdir=$inputdir/fixed

datefile=$basedir/scotscorr-letter-dates.tsv
wcfile=$scriptdir/scotscorr-wordcounts-nopunct.tsv

if [ ! -d $outputdir ]; then
    mkdir -p $outputdir
fi

for corp in "$@"; do
    file=$inputdir/$corp.vrt
    outfile=$outputdir/$(basename $file)
    $scriptdir/scotscorr-vrt-fix.pl $file |
    $scriptdir/scotscorr-vrt-fix-wc.pl <(cut -f4,5 $wcfile) |
    $scriptdir/scotscorr-vrt-add-orig-date.pl $datefile |
    $scriptdir/scotscorr-vrt-add-comments.pl > $outfile
done
