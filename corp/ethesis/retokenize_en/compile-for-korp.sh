
PATH=$PATH:/proj/clarin/korp/cwb/bin:/proj/clarin/korp/scripts

korp-make --corpus-root="/proj/clarin/korp/corpora" \
 --input-attributes="ref lemma pos xpos msd dephead deprel deps misc" \
  --compound-boundary-marker="#" --lemgram-posmap=lemgram_posmap_ud2_universal.tsv \
   --log-file=log --verbose CORPUSNAME ethesis_en/[gradut|vaitokset]/FACULTY/*.vrt

CORPUSNAME	  	        FACULTY

vaitokset
---------

ethesis_en_phd_mm_test		maajametsatiede
ethesis_en_phd_hum_test		humanistinen
ethesis_en_phd_bio_test		bio_ja_ymparistot
ethesis_en_phd_beh_test		kayttaytymistiede
ethesis_en_phd_ot_test		oikeustiede
ethesis_en_phd_med_test		laaketiede
ethesis_en_phd_far_test		farmasia
ethesis_en_phd_math_test	matemaattis # changed to sci
ethesis_en_phd_valt_test	valtiotiede
ethesis_en_phd_teo_test		teologinen
ethesis_en_phd_el_test		elainlaaketiede

gradut
------

ethesis_en_ma_mm_test		maajametsatiede 
ethesis_en_ma_ai_test		aleksanteri-instituutti
ethesis_en_ma_hum_test		humanistinen
ethesis_en_ma_bio_test		bio_ja_ymparistot
ethesis_en_ma_beh_test		kayttaytymistiede
ethesis_en_ma_far_test		farmasia
ethesis_en_ma_ot_test		oikeustiede
ethesis_en_ma_med_test		laaketiede
ethesis_en_ma_sci_test		matemaattis
ethesis_en_ma_valt_test		valtiotiede
ethesis_en_ma_teo_test		teologinen
ethesis_en_ma_el_test		elainlaaketiede

for faculty in "mm:maajametsatiede" "ai:aleksanteri-instituutti" "hum:humanistinen" "bio:bio_ja_ymparistot" "beh:kayttaytymistiede" "far:farmasia" "ot:oikeustiede" "med:laaketiede" "sci:matemaattis" "valt:valtiotiede" "teo:teologinen" "el:elainlaaketiede";
do
;	
done
