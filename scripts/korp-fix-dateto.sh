#! /bin/sh

# Fix invalid text_dateto dates (day 31 in months with fewer days) in
# Korp CWB data (and MySQL timedata tables)
#
# Usage: korp-fix-dateto.sh corpus_id ...
#
# This might be generalized to handle more invalid cases. Or would
# this functionality be more appropriate in korp-convert-timedata.sh?


progname=`basename $0`
progdir=`dirname $0`


. $progdir/korp-lib.sh


registry=$corpus_root/registry


fix_dateto () {
    corpus=$1
    if [ ! -e $registry/$corpus ]; then
	printf "Warning: Corpus $corpus not found in the CWB corpus registry\n"
	return
    elif ! grep -q text_dateto $registry/$corpus; then
	printf "Warning: Corpus $corpus has no text_dateto attribute\n"
	return
    fi
    printf "$corpus: "
    origfile=$tmp_prefix.text_dateto_orig.pos
    corrfile=$tmp_prefix.text_dateto_corr.pos
    $cwb_bindir/cwb-s-decode -r $registry $corpus -S text_dateto > $origfile
    if egrep -q '(0[469]|11)31$' $origfile; then
	printf "Fixing... "
	perl -pe '
            s/(0[469]|11)31$/${1}30/;
            ($y) = /\t(\d{4})\d{4}$/;
            $d = ($y % 4 == 0 && ($y % 100 != 0 || $y % 400 == 0)) ? "29" : "28";
            s/0231$/02$d/' $origfile > $corrfile
	datadir=$corpus_root/data/$corpus
	for suff in avs avx rng; do
	    fname=$datadir/text_dateto.$suff
	    cp -p --backup=numbered $fname $fname.bak
	done
	$cwb_bindir/cwb-s-encode -d $datadir -B -V text_dateto < $corrfile
	$progdir/korp-convert-timedata.sh --convert mysql,info $corpus
	printf "Done.\n"
    else
	printf "Ok.\n"
    fi
}


for corpus in "$@"; do
    fix_dateto $corpus
done
