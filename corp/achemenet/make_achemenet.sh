#!/bin/bash
# Process VRT files into CWB @ puhti
for filename in "$@"; do
    corpusname=$(basename $filename .vrt)
    corpusname=${corpusname/ach/achemenet}
    echo "$corpusname"
    /projappl/clarin/Kielipankki-utilities/scripts/korp-make --force --add-lemgrams-without-diacritics --add-lowercase-lemgrams --no-lemmas-without-boundaries --lemgram-posmap achemenet_lemgram_posmap.tsv $corpusname $filename
done
