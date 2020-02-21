#!/bin/sh

PATH=$PATH:/proj/clarin/korp/cwb/bin:/proj/clarin/korp/scripts
lemgram_posmap="lemgram_posmap.tsv"
corpusname="pabivus_"
corpusrootdir="/proj/clarin/korp/corpora"
# registrydir="/proj/clarin/korp/corpora/registry"
# scramble=""
# no compound boundary marker

# Unlinked versions

for lang in koi kpv krl mdf myv olo udm;
do
    korp-make --corpus-root=$corpusrootdir --input-attributes="ref lemma pos msd" \
	      --lemgram-posmap=$lemgram_posmap --log-file=log --verbose \
	      $corpusname$lang $lang/*.vrt;
done
