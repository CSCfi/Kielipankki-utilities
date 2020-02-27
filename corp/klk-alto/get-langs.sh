#!/bin/sh
#for dir in */; do
for dir in $1; do
    # todo: extension "mets.xml" is in some cases "METS.xml":
    # finclarin_puuttuneita/finclarin_siirto/[0355-3787|0356-1356|0356-1623|0357-1521]
    # and language is given in "<MODS:languageTerm" (it is in all seven cases 'fi')
    # todo: one metsfile has space in its name:
    # finclarin_1.7.2014-31.12.2014/finclarin_siirto/1458-2503/1888/alto/1124867_1458-2503_1888-04-04_90\ B_mets.xml
    # (The language is 'sv')
    for subdir in ${dir}/finclarin_siirto/*/*/; do ls ${subdir}alto/*mets.xml; done > metsfiles;
    for metsfile in `cat metsfiles`; do grep -m 1 'lang="' $metsfile | perl -pe 's/^.*lang="(..)".*$/\1/;'; done > langs;
    sort langs | uniq -c | sort -nr;
done
