#!/bin/sh

# copy files from IDA packages

verbose="false";
for arg in $@;
do
    if [ "$arg" = "--verbose" ]; then
	verbose="true";
    fi
done

for dir in gradut vaitokset;
do
    if (ls $dir > /dev/null 2> /dev/null); then
	echo "Directory "$dir" exists";
	exit 1;
    fi
done

if [ "$verbose" = "true" ]; then echo "Copying files from IDA packages"; fi

if !(ls gradut/ > /dev/null 2> /dev/null); then
    mkdir gradut ;
    cd gradut ;
    cp -R ../E-thesis_gradut_TXT_2016-11-22/* . ;
    cp ../E-thesis_other_langs_VRT_2016-11-22/ethesis_en_ma_mm.vrt maajametsatiede/metadata_vrt ;
    cp ../E-thesis_other_langs_VRT_2016-11-22/ethesis_en_ma_sci.vrt matemaattis/metadata_vrt ;
    cp ../E-thesis_other_langs_VRT_2016-11-22/ethesis_en_ma_valt.vrt valtiotiede/metadata_vrt ;
    cd .. ;
fi

if !(ls vaitokset/ > /dev/null 2> /dev/null); then
    mkdir vaitokset ;
    cd vaitokset ;
    cp -R ../E-thesis_vaitokset_TXT_2016-10-17/* . ;
    # harmonize directory names
    mv beh kayttaytymistiede ;
    mv bio bio_ja_ymparistot ;
    mv elain elainlaaketiede ;
    mv maajametsa maajametsatiede ;
    mv matematiikka matemaattis ;
    mv med laaketiede ;
    mv oikeus oikeustiede ;
    cd .. ;
fi

# harmonize metadata filenames
for file in gradut/*/logfile.txt;
do
    echo $file | perl -pe 's/^(.*)\/logfile\.txt$/mv \1\/logfile.txt \1\/metadata_txt/;' | sh;
done
for file in gradut/*/read.me;
do
    echo $file | perl -pe 's/^(.*)\/read\.me$/mv \1\/read.me \1\/metadata_txt/;' | sh;
done

# Fix typos in logfile:
cat vaitokset/laaketiede/logfile.txt | perl -pe 's/ xml\:lang=" / /; s/\@\@\@" xml\:lang=//;' > tmp;
mv tmp vaitokset/laaketiede/logfile.txt;

for file in vaitokset/*/logfile.txt;
do
    echo $file | perl -pe 's/^(.*)\/logfile\.txt$/mv \1\/logfile.txt \1\/metadata_txt/;' | sh;
done

for file in gradut/*/metadata_txt gradut/*/metadata_vrt vaitokset/*/metadata_txt ;
do
    cat $file | perl -pe "s/(\|\|\|<text )/\n\1/g;" > tmp;
    mv tmp $file;
done

# rename vaitokset/maajametsatiede/en_a_hammaslДДkmmoniae.txt, else korp-make gives an error:
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xd0 in position 47: ordinal not in range(128)
mv vaitokset/maajametsatiede/en_a_hammaslДДkmmoniae.txt vaitokset/maajametsatiede/en_a_hammaslaakmmoniae.txt
