#!/bin/bash
#prepares folder structure for Agricola


echo "haggai_GM.xml: cleans away empty spaces in attribute values"
perl -pe 's/(([^\"]*?)=\"([^\"]*?)) \"/$1\"/' haggai_GM.xml > haggai_GM_test.xml

rm haggai_GM.xml

mv haggai_GM_test.xml haggai_GM.xml


echo "ps_r_GM.xml: fix encoding"
perl -pe 's/(<\?xml .*?encoding=")iso-8859-1/$1utf-8/' ps_r_GM.xml > ps_r_GM_test.xml

rm ps_r_GM.xml

mv ps_r_GM_test.xml ps_r_GM.xml

echo "create subfolders"
mkdir abckiria
mkdir kasikiria
mkdir messu
mkdir piina
mkdir profeetat
mkdir psaltari
mkdir rucouskiria
mkdir sewsitestamenti
mkdir veisut 

echo "moves files into directories"
mv abc_GM.xml abckiria/
mv käs_*.xml kasikiria/
mv messu_*.xml messu/
mv piina_GM.xml piina/
mv haggai_*.xml profeetat/
mv mal_*.xml profeetat/
mv prof_*.xml profeetat/
mv sak_*.xml profeetat/
mv ps_*.xml psaltari/
mv rk_GM.xml rucouskiria/
mv veisut_*.xml veisut/
mv *.xml sewsitestamenti/




