#! /bin/sh

# Make a Korp corpus package for ScotsCorr, based on VRT files.
#
# Note that this script does not regenerate the word count file or
# documentation files.


progname=`basename $0`
progdir=`dirname $0`

scriptdir=$progdir/../../scripts


. $scriptdir/korp-lib.sh


add_line_attr () {
    local corp
    corp=$1
    {
	cwb-decode -n -C $corp -P word |
	grep '\\' |
	gawk '{print $1}'
	cwb-s-decode $corp -S text |
	cut -d"$tab" -f2
    } |
    sort -n -u |
    gawk 'BEGIN { b = 0 }
          { print b "\t" $1; b = $1 + 1 }' |
    cwb-s-encode -d /v/corpora/data/$corp -S line
}

fixed_vrtdir=/v/corpora/src/scotscorr/vrt/fixed

corpora=$(list_corpora scots_* | grep -v "1550")

for corp in $corpora; do
    ./scotscorr-vrt-fix-all.sh $corp
    $scriptdir/korp-make --force --input-attrs comment \
	--add-structure-ids "sentence paragraph" --no-name-attrs --no-package \
	--verbose --corpus-id $corp $fixed_vrtdir/$corp.vrt
    add_line_attr $corp
    cwb_registry_add_structattr $corp line
done

$scriptdir/korp-make-corpus-package.sh --database-format tsv \
    --tsv-dir /v/corpora/vrt/{corpid} scotscorr $corpora
