#!/bin/sh

PATH=$PATH:/proj/clarin/korp/cwb/bin:/proj/clarin/korp/scripts
lemgram_posmap="lemgram_posmap.tsv"
corpusname="pabivus"
corpusrootdir="/proj/clarin/korp/corpora"
registrydir="/proj/clarin/korp/corpora/registry"
# scramble=""
# no compound boundary marker

# Linked versions for languages that are available for all books
# (unlinked: same but without --no-package)

if [ "foo" = "bar" ]; then

for lang_year in "fin_1938" "koi_2019" "kpv_2008" "krl_2011" "mdf_2016" "myv_2006" "olo_2003" "udm_1997";
do
    echo "Compiling "${corpusname}_${lang_year}"...";
    if [ "$1" != "--dry-run" ]; then
	korp-make --force --no-package --corpus-root=${corpusrootdir} --input-attributes="ref lemma pos msd" \
	    --lemgram-posmap=${lemgram_posmap} --log-file=log --verbose \
	    ${corpusname}_${lang_year} ${corpusname}_${lang_year}.vrt;
    fi
done



# Linked versions for languages that are available for some books
# (unlinked: same but without --no-package)

for lang_year_files in "koi_1996:koi/koi-42_MRK-1996_vrt.vrt" \
    "kpv_1995:kpv/kpv-42_MRK-1995_vrt.vrt" \
    "kpv_1997:kpv/kpv-44_JHN-1997_vrt.vrt" \
    "mdf_1995:mdf/mdf-42_MRK-1995_vrt.vrt" \
    "myv_1821:myv/myv-41_MAT-1821_vrt.vrt" \
    "myv_1910:myv/myv-41_MAT-1910_vrt.vrt" \
    "myv_1998:myv/myv-41_MAT-1998_vrt.vrt" \
    "myv_1995:myv/myv-42_MRK-1995_vrt.vrt" \
    "myv_1996:myv/myv-43_LUK-1996_vrt.vrt myv/myv-45_ACT-1996_vrt.vrt";
do
    lang_year=`echo ${lang_year_files} | cut -f1 -d':'`;
    files=`echo ${lang_year_files} | cut -f2 -d':'`;
    echo "Compiling "${corpusname}_${lang_year}"...";
    if [ "$1" != "--dry-run" ]; then
	korp-make --force --no-package --corpus-root=${corpusrootdir} --input-attributes="ref lemma pos msd" \
	    --lemgram-posmap=${lemgram_posmap} --log-file=log --verbose \
	    ${corpusname}_${lang_year} ${files};
    fi
done

# Link all subcorpora with each other

for lang_year_1 in "fin_1938" "koi_1996" "koi_2019" "kpv_1995" "kpv_1997" "kpv_2008" "krl_2011" "mdf_1995" "mdf_2016" "myv_1821" "myv_1910" "myv_1995" "myv_1996" "myv_1998" "myv_2006" "olo_2003" "udm_1997";
do
    for lang_year_2 in "fin_1938" "koi_1996" "koi_2019" "kpv_1995" "kpv_1997" "kpv_2008" "krl_2011" "mdf_1995" "mdf_2016" "myv_1821" "myv_1910" "myv_1995" "myv_1996" "myv_1998" "myv_2006" "olo_2003" "udm_1997";
    do
	if [[ "$lang_year_2" > "$lang_year_1" ]]; then
	    echo "Linking "${corpusname}_${lang_year_1}" with "${corpusname}_${lang_year_2}"...";
	    if [ "$1" != "--dry-run" ]; then
		cwb-align -v -r $registrydir -o ${corpusname}_${lang_year_1}_${lang_year_2}.align -V link_id ${corpusname}_${lang_year_1} ${corpusname}_${lang_year_2} link;
		cwb-align -v -r $registrydir -o ${corpusname}_${lang_year_2}_${lang_year_1}.align -V link_id ${corpusname}_${lang_year_2} ${corpusname}_${lang_year_1} link;
		cwb-regedit -r $registrydir ${corpusname}_${lang_year_1} :add :a ${corpusname}_${lang_year_2};
		cwb-regedit -r $registrydir ${corpusname}_${lang_year_2} :add :a ${corpusname}_${lang_year_1};
		cwb-align-encode -v -r $registrydir -D ${corpusname}_${lang_year_1}_${lang_year_2}.align;
		cwb-align-encode -v -r $registrydir -D ${corpusname}_${lang_year_2}_${lang_year_1}.align;
	    fi
	fi;
    done;
done

fi

#for versions in "koi_2019:koi_1996" "kpv_2008:kpv_1995 kpv_1997" "mdf_2016:mdf_1995" "myv_2006:myv_1996 myv_1995 myv_1998 myv_1910 myv_1821";
#do
#    lang_year_1s=`echo $versions | cut -f1 -d':'`;
#    lang_year_1s=${lang_year_1s}" fin_test";
#    lang_year_2s=`echo $versions | cut -f2 -d':'`;
#    for lang_year_1 in ${lang_year_1s};
#    do
#	for lang_year_2 in ${lang_year_2s};
#	do
#	    echo "Linking "${corpusname}_${lang_year_1}" with "${corpusname}_${lang_year_2}"...";
#	    cwb-align -v -r $registrydir -o ${corpusname}_${lang_year_1}_${lang_year_2}.align -V link_id ${corpusname}_${lang_year_1} ${corpusname}_${lang_year_2} link;
#	    cwb-align -v -r $registrydir -o ${corpusname}_${lang_year_2}_${lang_year_1}.align -V link_id ${corpusname}_${lang_year_2} ${corpusname}_${lang_year_1} link;
#	    cwb-regedit -r $registrydir ${corpusname}_${lang_year_1} :add :a ${corpusname}_${lang_year_2};
#	    cwb-regedit -r $registrydir ${corpusname}_${lang_year_2} :add :a ${corpusname}_${lang_year_1};
#	    cwb-align-encode -v -r $registrydir -D ${corpusname}_${lang_year_1}_${lang_year_2}.align;
#	    cwb-align-encode -v -r $registrydir -D ${corpusname}_${lang_year_2}_${lang_year_1}.align;
#	done;
#   done;
#done

if [ "$1" != "--dry-run" ]; then
    korp-make-corpus-package.sh --target-corpus-root=/v/corpora --corpus-root=$corpusrootdir \
	--database-format tsv --include-vrt-dir ${corpusname}_par \
	${corpusname}_fin_1938 ${corpusname}_koi_2019 ${corpusname}_kpv_2008 ${corpusname}_krl_2011 ${corpusname}_mdf_2016 \
	${corpusname}_myv_2006 ${corpusname}_olo_2003 ${corpusname}_udm_1997 ${corpusname}_koi_1996 ${corpusname}_kpv_1995 \
	${corpusname}_kpv_1997 ${corpusname}_mdf_1995 ${corpusname}_myv_1996 ${corpusname}_myv_1995 ${corpusname}_myv_1998 \
	${corpusname}_myv_1910 ${corpusname}_myv_1821;
fi
