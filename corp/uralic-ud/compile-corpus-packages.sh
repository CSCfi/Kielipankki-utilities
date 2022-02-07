#!/bin/sh

PATH=$PATH:/projappl/clarin/cwb/bin/:/projappl/clarin/cwb-perl/bin/:/projappl/clarin/Kielipankki-utilities/scripts/
export PERL5LIB=/projappl/clarin/cwb-perl/lib/site_perl
corpusrootdir="/scratch/clarin/corpora"
# registrydir="/scratch/clarin/corpora/registry"

corpora=( 'uralic_ud_v29_myv_jr,UD_Erzya-JR_v2.9.vrt'
'uralic_ud_v29_et_edt,UD_Estonian-EDT_v2.9.vrt'
'uralic_ud_v29_et_ewt,UD_Estonian-EWT_v2.9.vrt'
'uralic_ud_v29_fi_ftb,UD_Finnish-FTB_v2.9.vrt'
'uralic_ud_v29_fi_ood,UD_Finnish-OOD_v2.9.vrt'
'uralic_ud_v29_fi_pud,UD_Finnish-PUD_v2.9.vrt'
'uralic_ud_v29_fi_tdt,UD_Finnish-TDT_v2.9.vrt'
'uralic_ud_v29_hu_szeged,UD_Hungarian-Szeged_v2.9.vrt'
'uralic_ud_v29_krl_kkpp,UD_Karelian-KKPP_v2.9.vrt'
'uralic_ud_v29_koi_uh,UD_Komi_Permyak-UH_v2.9.vrt'
'uralic_ud_v29_kpv_ikdp,UD_Komi_Zyrian-IKDP_v2.9.vrt'
'uralic_ud_v29_kpv_lattice,UD_Komi_Zyrian-Lattice_v2.9.vrt'
'uralic_ud_v29_olo_kkpp,UD_Livvi-KKPP_v2.9.vrt'
'uralic_ud_v29_mdf_jr,UD_Moksha-JR_v2.9.vrt'
'uralic_ud_v29_sme_giella,UD_North_Sami-Giella_v2.9.vrt'
'uralic_ud_v29_sms_giellagas,UD_Skolt_Sami-Giellagas_v2.9.vrt' );

for corpus in ${corpora[@]};
do
    corpus=`echo $corpus | tr ',' ' '`;
    korp-make --corpus-root=$corpusrootdir --lemgram-posmap="lemgram_posmap_ud2_universal.tsv" --log-file=log --verbose $corpus;
done
