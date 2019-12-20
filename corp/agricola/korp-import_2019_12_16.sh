#! /bin/bash

for SUB in abckiria kasikiria messu piina profeetat psaltari rucouskiria sewsitestamenti veisut ; do
    CNAME=agricola_test_$SUB
    /proj/clarin/korp/scripts/korp-make --force --input-fields "lemma pos nrm type mrp fun com tunit" --lemgram-posmap /proj/clarin/korp/git-work/Kielipankki-konversio/corp/agricola/agricola-lemgram_posmap.tsv $CNAME vrt/$SUB/*.vrt
done
