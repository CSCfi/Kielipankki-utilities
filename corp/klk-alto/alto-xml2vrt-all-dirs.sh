#!/bin/sh

game="/scratch/clarin/USERNAME/Kielipankki-utilities/vrt-tools/game"
xml_to_vrt_dir="/scratch/clarin/USERNAME/finclarin_siirto/alto-xml2vrt-dir.sh"

for dir in */*/alto;
do
    size=`du --max-depth=0 $dir | cut -f1`;
    hours="1";
    if [ "$size" -gt "100000" ]; then
	hours="2";
    fi
    if [ "$size" -gt "300000" ]; then
	hours="3";
    fi
    if [ "$size" -gt "600000" ]; then
	hours="4";
    fi
    cd $dir;
    echo $game --hours $hours --log=log $xml_to_vrt_dir;
    cd ../../..;
done
