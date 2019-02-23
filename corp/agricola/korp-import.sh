#! /bin/bash

for SUB in abckiria kasikiria messu piina profeetat psaltari rucouskiria sewsitestamenti veisut ; do
    CNAME=agricola_$SUB
    /proj/clarin/korp/scripts/korp-make --input-fields "lemma pos nrm type mrp fun com tunit" $CNAME vrt/$SUB/*.vrt
done
