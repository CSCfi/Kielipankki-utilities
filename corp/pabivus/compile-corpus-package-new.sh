#!/bin/sh

PATH=$PATH:/projappl/clarin/cwb/bin/:/projappl/clarin/cwb-perl/bin/:/projappl/clarin/Kielipankki-utilities/scripts/
export PERL5LIB=/projappl/clarin/cwb-perl/lib/site_perl
corpusrootdir="/scratch/clarin/corpora"
registrydir="/scratch/clarin/corpora/registry"

for lang_year in "fin_1938" "kca_2013" "kca_2017" "kca_2018" "koi_1996" "koi_2019" "kpv_1995" "kpv_1997" "kpv_2008" \
    "krl_2011" "mdf_1995" "mdf_2016" "mns_2000" "myv_1821" "myv_1910" "myv_1995" "myv_1996" "myv_1998" "myv_2006" \
    "myv_2011" "myv_2020" "olo_2003" "rus_1876" "udm_1997" "vep_2013";
do
    lemgram_posmap="lemgram_posmap.tsv";
    if (echo "${lang_year}" | egrep 'fin_|mdf_|myv_' &> /dev/null); then
	lemgram_posmap="../iijoki-tnpp/lemgram_posmap_ud2_universal.tsv";
    fi
    echo "Compiling pabivus_"${lang_year}" using lemgram_posmap "${lemgram_posmap}"...";
    if [ "$1" != "--dry-run" ]; then
	korp-make --force --no-package --corpus-root=${corpusrootdir} --compound-boundary-marker="#" \
	    --lemgram-posmap=${lemgram_posmap} --log-file=log --verbose \
	    pabivus_${lang_year} pabivus_${lang_year}.vrt;
    fi
done

for lang_year_1 in "fin_1938" "kca_2013" "kca_2017" "kca_2018" "koi_1996" "koi_2019" "kpv_1995" "kpv_1997" "kpv_2008" \
    "krl_2011" "mdf_1995" "mdf_2016" "mns_2000" "myv_1821" "myv_1910" "myv_1995" "myv_1996" "myv_1998" "myv_2006" \
    "myv_2011" "myv_2020" "olo_2003" "rus_1876" "udm_1997" "vep_2013";
do
    for lang_year_2 in "fin_1938" "kca_2013" "kca_2017" "kca_2018" "koi_1996" "koi_2019" "kpv_1995" "kpv_1997" "kpv_2008" \
	"krl_2011" "mdf_1995" "mdf_2016" "mns_2000" "myv_1821" "myv_1910" "myv_1995" "myv_1996" "myv_1998" "myv_2006" \
	"myv_2011" "myv_2020" "olo_2003" "rus_1876" "udm_1997" "vep_2013";
    do
	if [[ "$lang_year_2" > "$lang_year_1" ]]; then
	    echo "Linking pabivus_"${lang_year_1}" with pabivus_"${lang_year_2}"...";
	    if [ "$1" != "--dry-run" ]; then
		cwb-align -v -r $registrydir -o "pabivus_"${lang_year_1}_${lang_year_2}.align -V link_id "pabivus_"${lang_year_1} "pabivus_"${lang_year_2} link;
		cwb-align -v -r $registrydir -o "pabivus_"${lang_year_2}_${lang_year_1}.align -V link_id "pabivus_"${lang_year_2} "pabivus_"${lang_year_1} link;
		cwb-regedit -r $registrydir "pabivus_"${lang_year_1} :add :a "pabivus_"${lang_year_2};
		cwb-regedit -r $registrydir "pabivus_"${lang_year_2} :add :a "pabivus_"${lang_year_1};
		cwb-align-encode -v -r $registrydir -D "pabivus_"${lang_year_1}_${lang_year_2}.align;
		cwb-align-encode -v -r $registrydir -D "pabivus_"${lang_year_2}_${lang_year_1}.align;
	    fi
	fi;
    done;
done

if [ "$1" != "--dry-run" ]; then
    korp-make-corpus-package.sh --target-corpus-root=/v/corpora --corpus-root=$corpusrootdir \
				--database-format tsv --include-vrt-dir "pabivus_par" \
				"pabivus_fin_1938" "pabivus_kca_2013" "pabivus_kca_2017" "pabivus_kca_2018" "pabivus_koi_1996" "pabivus_koi_2019" \
				"pabivus_kpv_1995" "pabivus_kpv_1997" "pabivus_kpv_2008" "pabivus_krl_2011" "pabivus_mdf_1995" "pabivus_mdf_2016" \
				"pabivus_mns_2000" "pabivus_myv_1821" "pabivus_myv_1910" "pabivus_myv_1995" "pabivus_myv_1996" "pabivus_myv_1998" \
				"pabivus_myv_2006" "pabivus_myv_2011" "pabivus_myv_2020" "pabivus_olo_2003" "pabivus_rus_1876" "pabivus_udm_1997" "pabivus_vep_2013";
fi
