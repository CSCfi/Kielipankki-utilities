#!/bin/sh

# Location of Kielipankki-utilities directory.
scriptdir="."
# Where VRT files are copied. If empty, no copying is done.
outputdir=""
# The linking file in csv format.
linkingfile="FILENAME.csv"

convpy=$scriptdir"/Kielipankki-utilities/corp/klk-alto/conv-new.py";
mets2metadata=$scriptdir"/Kielipankki-utilities/corp/klk-alto/mets2metadata.py";
vrtvalidate=$scriptdir"/Kielipankki-utilities/vrt-tools/vrt-validate";

for dir in $1;
do
    for metsfile in $dir/*_mets.xml;
    do
	# extract metadata from mets and linking files
	metadatafile=`echo $metsfile | perl -pe 's/_mets\.xml/\.metadata/;'`;
	echo "Generating "$metadatafile;
	$mets2metadata $metsfile $linkingfile > $metadatafile;
	# extract language used
	lang="";
	if [ "$outputdir" != "" ]; then
	    lang=`grep 'language' $metadatafile | perl -pe "s/^.*'language'\: '([^']+)'.*$/\1/;"`;
	    echo "Language: "$lang;
	    if ! [ -d "$outputdir/$lang" ]; then
		mkdir $outputdir/$lang;
	    fi
	fi
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
		vrtfile=$vrtfile.empty
	    else
		echo "Validating result";
		$vrtvalidate $vrtfile -o tmp;
		lines=`cat tmp | wc -l`;
		if [ "$lines" -gt "1" ]; then
		    cat tmp;
		    echo "Not valid VRT format, exiting.";
		    exit 1;
		fi
	    fi
	    if [ "$outputdir" != "" ]; then
		cp --parents $vrtfile $outputdir/$lang/;
	    fi
	done
    done
done
