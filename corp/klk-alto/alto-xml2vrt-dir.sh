#!/bin/sh

convpy="/scratch/clarin/USERNAME/Kielipankki-utilities/corp/klk-alto/conv.py";
vrtvalidate="/scratch/clarin/USERNAME/Kielipankki-utilities/vrt-tools/vrt-validate";

for xmlfile in $1/*.xml;
do
    if !(echo $xmlfile | grep 'mets\.xml' > /dev/null 2> /dev/null); then
	metsfile=`echo $xmlfile | perl -pe 's/page\-[0-9]+/mets/'`;
	if !(ls $metsfile > /dev/null 2> /dev/null); then
	    echo "Metsfile "$metsfile" not found, exiting.";
	    exit 1;
	else
	    echo "Using metsfile "$metsfile;
	fi
	vrtfile=`echo $xmlfile | perl -pe 's/\.xml/\.vrt/'`;
	echo "Generating "$vrtfile;
	$convpy --mets $metsfile $xmlfile > $vrtfile
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
    fi
done
