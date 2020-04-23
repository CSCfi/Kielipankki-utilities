#!/bin/sh

convpy="Kielipankki-utilities/corp/klk-alto/conv-new.py";
mets2metadata="Kielipankki-utilities/corp/klk-alto/mets2metadata.py";
linkingfile="FILENAME.csv"
vrtvalidate="Kielipankki-utilities/vrt-tools/vrt-validate";

for dir in $1;
do
    for metsfile in $dir/*_mets.xml;
    do
	# extract metadata from mets and linking files
	metadatafile=`echo $metsfile | perl -pe 's/_mets\.xml/\.metadata/;'`;
	echo "Generating "$metadatafile;
	$mets2metadata $metsfile $linkingfile > $metadatafile;
	# process all xml files that use the current mets file
	xmlfiles=`echo $metsfile | perl -pe 's/_mets\.xml/_page-*.xml/;'`
	for xmlfile in $xmlfiles;
	do
	    vrtfile=`echo $xmlfile | perl -pe 's/\.xml/\.vrt/'`;
	    echo "Generating "$vrtfile;
	    $convpy --metadata $metadatafile --metsfilename $metsfile $xmlfile > $vrtfile
	    lines=`cat $vrtfile | wc -l`;
	    if [ "$lines" = "1" ]; then
		echo "Empty VRT file, renaming *.vrt -> *.vrt.empty";
		mv $vrtfile $vrtfile.empty;
	    else
		echo "Validating result";
		if !($vrtvalidate $vrtfile); then
		    echo "Not valid VRT format, exiting.";
		    exit 1;
		fi
	    fi
	done
    done
done
