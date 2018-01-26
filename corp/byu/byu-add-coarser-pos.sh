#! /bin/sh


# Add a coarser part of speech to the BYU corpora.
#
# Usage: byu-add-coarser-pos.sh corpus ...


progdir=$(dirname $0)
progname=$(basename $0)

scriptdir=$progdir/../../scripts

. $scriptdir/korp-lib.sh


make_coarser_pos=$progdir/byu-make-coarser-pos.py
cwbdata_add_attrs=$scriptdir/cwbdata-add-attrs.sh

mapping_file_src=$progdir/byu-ud2-posmap.tsv
mapping_file=$tmp_prefix.map.tsv
cut -f1,3,4 $mapping_file_src > $mapping_file

corpora=$(list_corpora "$@")


add_coarser_pos () {
    local corp
    corp=$1
    $cwbdata_add_attrs --input-attrs "pos" \
	--new-attrs "pos/ pos_major/ msd_ambig" \
	--generator "$make_coarser_pos --output-stripped-pos $mapping_file" \
	--verbose $corp
}


for corp in $corpora; do
    add_coarser_pos $corp
done
