#!/bin/sh
# PATH=$PATH:/proj/clarin/korp/cwb/bin:/proj/clarin/korp/scripts
for corpusname in \
    wanca_test_fit_multili \
    wanca_test_fkv_multili \
    wanca_test_izh \
    wanca_test_kca_multili \
    wanca_test_koi_multili \
    wanca_test_kpv_multili \
    wanca_test_krl_multili \
    wanca_test_liv \
    wanca_test_lud \
    wanca_test_mdf_multili \
    wanca_test_mhr_multili \
    wanca_test_mns_multili \
    wanca_test_mrj_multili \
    wanca_test_myv_multili \
    wanca_test_nio \
    wanca_test_olo_multili \
    wanca_test_sjd \
    wanca_test_sjk \
    wanca_test_sju \
    wanca_test_sma_multili \
    wanca_test_sme_multili \
    wanca_test_smj_multili \
    wanca_test_smn_multili \
    wanca_test_sms_multili \
    wanca_test_udm_multili \
    wanca_test_vep_multili \
    wanca_test_vot \
    wanca_test_vro_multili \
    wanca_test_yrk
do
    korp-make --force --corpus-root="/proj/clarin/korp/corpora" --corpus-date unknown --log-file=log --verbose --input-attributes="spaces ref" $corpusname $corpusname.vrt;
done
