#!/bin/sh

PATH=$PATH:/proj/clarin/korp/cwb/bin:/proj/clarin/korp/scripts
lemgram_posmap="lemgram_posmap.tsv"
corpusname="pabivus_"
corpusrootdir="/proj/clarin/korp/corpora"
# registrydir="/proj/clarin/korp/corpora/registry"
# scramble=""
# no compound boundary marker

# Unlinked versions

for lang_year in "koi_2019" "kpv_2008" "krl_2011" "mdf_2016" "myv_2006" "olo_2003" "udm_1997";
do
    lang=`echo $lang_year | cut -f1 -d'_'`;
    year=`echo $lang_year | cut -f2 -d'_'`;
    korp-make --corpus-root=${corpusrootdir} --input-attributes="ref lemma pos msd" \
	      --lemgram-posmap=${lemgram_posmap} --log-file=log --verbose \
	      ${corpusname}${lang_year} ${lang}/*-${year}_.vrt;
done
