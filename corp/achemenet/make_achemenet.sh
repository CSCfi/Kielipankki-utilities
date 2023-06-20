#!/bin/bash
# Process VRT files into CWB @ puhti
for filename in *.vrt; do
    corpusname=${filename%%.*}
    echo "$corpusname"
    /projappl/clarin/Kielipankki-utilities/scripts/korp-make --force --input-fields "lemma translation sense transcription pos oraccpos normname lang msd autolemma url" --add-lemgrams-without-diacritics --add-lowercase-lemgrams --no-lemmas-without-boundaries --lemgram-posmap achemenet_lemgram_posmap.tsv $corpusname $filename
done
