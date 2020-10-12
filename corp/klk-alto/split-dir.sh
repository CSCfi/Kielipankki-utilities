#!/bin/sh

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo "split-dir.sh DIR THRESHOLD"
    echo "Split directory DIR into directories smaller than THRESHOLD kilobytes."
    echo "The new directories will be named alto_1, alto2, ..."
    exit 0;
fi

kbytes=0;
threshold=$2;
subdir_N=1;
subdir_prefix="alto_";

for metsfile in $1/*_mets.xml;
do
    # process all xml files that use the current mets file
    xmlfiles=`echo $metsfile | perl -pe 's/_mets\.xml/_page-*.xml/;'`
    more_kbytes=`du -c -k -d 0 $xmlfiles $metsfile | tail -1 | cut -f1`;
    kbytes=$((kbytes+more_kbytes));
    if [ "$kbytes" -gt "$threshold" ]; then
	subdir_N=$((subdir_N+1));
	kbytes=$more_kbytes;
    fi
    subdir=$1"/../"$subdir_prefix$subdir_N"/";
    if ! [ -d "$subdir" ]; then
	mkdir $subdir;
	echo "Created directory $subdir";
    fi
    cp $metsfile $subdir;

    for xmlfile in $xmlfiles;
    do
	cp $xmlfile $subdir;
    done

done
