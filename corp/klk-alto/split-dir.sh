#!/bin/sh

subdir_N=0;
subdir_prefix="subdir_";

for metsfile in $1/*_mets.xml;
do
    # process all xml files that use the current mets file
    xmlfiles=`echo $metsfile | perl -pe 's/_mets\.xml/_page-*.xml/;'`
    subdir_N=$((subdir_N+1));
    subdir=$1"/"$subdir_prefix$subdir_N"/";
    mkdir $subdir;
    mv $metsfile $subdir;
    for xmlfile in $xmlfiles;
    do
	mv $xmlfile $subdir;
    done
done
