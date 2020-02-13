
PATH=$PATH:/proj/clarin/korp/cwb/bin:/proj/clarin/korp/scripts

# "|" is used in lemmas, so "#" is defined as compund boundary marker instead (it is not used in lemmas)
korp-make --corpus-root="/proj/clarin/korp/corpora" --input-attributes="ref lemma msd" --compound-boundary-marker="#" --log-file=log --verbose komi_ikdp_test *.vrt
