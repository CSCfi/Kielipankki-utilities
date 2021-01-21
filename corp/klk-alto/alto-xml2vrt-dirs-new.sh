#!/bin/sh

# Location of Kielipankki-utilities directory.
scriptdir="."
# Where VRT files are copied. If empty, no copying is done.
outputdir=""
# Whether all VRT files are copied or just the single file
# (a concatenation of all VRT files that use the same metadata file)
copy_all_vrtfiles="false"
# The linking file in csv format.
linkingfile="FILENAME.csv"

convpy=$scriptdir"/corp/klk-alto/conv-new.py";
mets2metadata=$scriptdir"/corp/klk-alto/mets2metadata.py";
vrtfix=$scriptdir"/vrt-tools/vrt-fix-characters --control --private --nonchar --reserved --surrogate";
vrtfix_1="$vrtfix --replace=vanish --field=word --field=hyph"; # remove problematic characters for word and hyph
vrtfix_2="$vrtfix --field=content"; # replace problematic characters with '_' for content
vrtvalidate=$scriptdir"/vrt-tools/vrt-validate";

for dir in $1;
do
    xml_format_checked="false";
    for metsfile in $dir/*_mets.xml;
    do
	# extract metadata from mets and linking files
	metadatafile=`echo $metsfile | perl -pe 's/_mets\.xml/\.metadata/;'`;
	echo "Generating "$metadatafile;
	if !($mets2metadata $metsfile $linkingfile > $metadatafile); then
	    echo "Metadata file could not be created, exiting.";
	    exit 1;
	fi
	# extract language used
	lang="";
	if [ "$outputdir" != "" ]; then
	    if ! [ -d "$outputdir" ]; then
		mkdir $outputdir;
	    fi
	    lang=`grep 'language' $metadatafile | perl -pe "s/^.*'language'\: '([^']+)'.*$/\1/;"`;
	    echo "Language: "$lang;
	    if ! [ -d "$outputdir/$lang" ]; then
		mkdir $outputdir/$lang;
	    fi
	fi
	# process all xml files that use the current mets file
	# concatenate the resulting vrt files into a single file
	# (named *.VRT and renamed to *.vrt when copied)
	xmlfiles=`echo $metsfile | perl -pe 's/_mets\.xml/_page-*.xml/;'`
	single_vrtfile=`echo $metsfile | perl -pe 's/_mets\.xml/.VRT/;'`
	single_vrtfile_copied=`echo $metsfile | perl -pe 's/_mets\.xml/.vrt/;'`
	first_vrtfile="true";
	for xmlfile in $xmlfiles;
	do
	    # Check format of first XML file in directory
	    if [ "$xml_format_checked" = "false" ]; then
		if (grep -m 1 '<root>' $xmlfile > /dev/null); then
		    echo 'Error: $xmlfile has wrong XML format, skipping directory $dir.';
		    break;
		else
		    xml_format_checked="true";
		fi
	    fi
	    vrtfile=`echo $xmlfile | perl -pe 's/\.xml/\.vrt/'`;
	    echo "Generating "$vrtfile;
	    if !($convpy --metadata $metadatafile --metsfilename $metsfile $xmlfile > $vrtfile); then
		echo "VRT file could not be created, exiting.";
		exit 1;
	    fi
	    lines=`cat $vrtfile | wc -l`;
	    if [ "$lines" = "1" ]; then
		echo "Empty VRT file, renaming *.vrt -> *.vrt.empty";
		mv $vrtfile $vrtfile.empty;
		vrtfile=$vrtfile.empty
	    else
		$vrtfix_1 $vrtfile > $dir/tmp;
		$vrtfix_2 $dir/tmp > $vrtfile;
		echo "Validating result";
		$vrtvalidate $vrtfile -o $dir/tmp;
		lines=`cat $dir/tmp | wc -l`;
		if [ "$lines" -gt "1" ]; then
		    cat $dir/tmp;
		    echo "Not valid VRT format, exiting.";
		    exit 1;
		fi
		# concatenate into single vrt file
		if [ "$first_vrtfile" = "true" ]; then
		    cp $vrtfile $single_vrtfile;
		    first_vrtfile="false";
		else
		    # skip "<!--" vrt line
		    cat $vrtfile | tail --lines=+2 >> $single_vrtfile;
		fi
	    fi
	    if [ "$outputdir" != "" -a "$copy_all_vrtfiles" = "true" ]; then
		cp --parents $vrtfile $outputdir/$lang/;
	    fi
	done
	# If first XML file in directory had wrong format, skip the whole directory
	if [ "$xml_format_checked" = "false" ]; then
	    break;
	fi
	if [ "$outputdir" != "" ]; then
	    cp --parents $single_vrtfile $outputdir/$lang/;
	    # rename *.VRT to *.vrt
	    mv $outputdir/$lang/$single_vrtfile $outputdir/$lang/$single_vrtfile_copied;
	fi
    done
done
