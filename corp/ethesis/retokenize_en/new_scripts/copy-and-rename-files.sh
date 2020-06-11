#!/bin/sh

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo """
copy-and-rename-files.sh [TARGETDIR]

Copy and renames files from IDA E-thesis packages
E-thesis_gradut_TXT_2016-11-22.zip and
E-thesis_vaitokset_TXT_2016-10-17.zip under TARGETDIR.

The script assumes that the packages have been extracted
under directories E-thesis_gradut_TXT_2016-11-22 and
E-thesis_vaitokset_TXT_2016-10-17.
""";
    exit 0;
fi

targetdir=$1;

for sourcedir in E-thesis_gradut_TXT_2016-11-22 E-thesis_vaitokset_TXT_2016-10-17;
do
    if !(ls $sourcedir > /dev/null 2> /dev/null); then
	echo "Source directory "$sourcedir" not found, exiting."
	exit 1;
    fi
done

if [ "$targetdir" = "" ]; then
    echo "No TARGETDIR given, exiting.";
    exit 1;
fi
if (ls $targetdir > /dev/null 2> /dev/null); then
    echo "TARGETDIR "$targetdir" exists, exiting.";
    exit 1;
fi
mkdir $targetdir;

cd $targetdir;

cp -R ../E-thesis_gradut_TXT_2016-11-22/*/ . ;
# rename directory names
mv aleksanteri-instituutti ethesis_en_ma_ai;
mv kayttaytymistiede ethesis_en_ma_beh;
mv bio_ja_ymparistot ethesis_en_ma_bio;
mv elainlaaketiede ethesis_en_ma_el;
mv farmasia ethesis_en_ma_far;
mv humanistinen ethesis_en_ma_hum;
mv laaketiede ethesis_en_ma_med;
mv maajametsatiede ethesis_en_ma_mm;
mv oikeustiede ethesis_en_ma_ot;
mv matemaattis ethesis_en_ma_sci;
mv teologinen ethesis_en_ma_teo;
mv valtiotiede ethesis_en_ma_valt;  

cp -R ../E-thesis_vaitokset_TXT_2016-10-17/*/ . ;
# rename directory names
mv beh ethesis_en_phd_beh;
mv bio ethesis_en_phd_bio;
mv elain ethesis_en_phd_el;
mv farmasia ethesis_en_phd_far;
mv humanistinen ethesis_en_phd_hum;
mv maajametsa ethesis_en_phd_mm;
mv matematiikka ethesis_en_phd_math;
mv med ethesis_en_phd_med;
mv oikeus ethesis_en_phd_ot;
mv teologinen ethesis_en_phd_teo;
mv valtiotiede ethesis_en_phd_valt;

# rename vaitokset/maajametsatiede/en_a_hammaslДДkmmoniae.txt, else korp-make gives an error:
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xd0 in position 47: ordinal not in range(128)
mv ethesis_en_phd_mm/en_a_hammaslДДkmmoniae.txt ethesis_en_phd_mm/en_a_hammaslaakmmoniae.txt;

# rename some files that actually contain English
mv ethesis_en_ma_sci/fi_e_2011-05-31xactbou.txt ethesis_en_ma_sci/en_e_2011-05-31xactbou.txt
mv ethesis_en_ma_sci/fi_e_2011-06-08ffectof.txt ethesis_en_ma_sci/en_e_2011-06-08ffectof.txt # Finnish abstract
# mv ethesis_en_phd_hum/other_s_2006-12-02ubstrat.txt ethesis_en_phd_hum/en_s_2006-12-02ubstrat.txt ?
mv ethesis_en_ma_valt/fi_r_2013-06-10esident.txt ethesis_en_ma_valt/en_r_2013-06-10esident.txt

# todo: also change lang="en" in metadata of these files

# Remove " (2)" from filenames in */*.txt and append ".orig"
# to the filenames without " (2)":
# "FILENAME.txt" -> "FILENAME.txt.orig"
# "FILENAME (2).txt" -> "FILENAME.txt"
ls */*" (2)".txt | perl -pe 'chomp(); my $newname = $_; $newname =~ s/ \(2\)//; my $oldname=$_; print "mv \"".$newname."\" \"".$newname.".orig\""."\n"; print "mv \"".$oldname."\" \"".$newname."\"\n"; $_="";' | sh ;

cd .. ;
