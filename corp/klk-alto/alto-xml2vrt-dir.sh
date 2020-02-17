#!/bin/sh

convpy="";
vrtvalidate="";

for xmlfile in *.xml;
do
    if !(echo $xmlfile | grep 'mets\.xml' > /dev/null 2> /dev/null); then
	if !(echo $xmlfile | egrep 'page\-[0-9]+\.xml' > /dev/null 2> /dev/null); then
	    echo "Error: XML file "$xmlfile" does not have page defined in its name, exiting.";
	    exit 1;
	fi
	metsfile=`echo $xmlfile | perl -pe 's/page\-[0-9]+\.xml/mets.xml/'`;
	if !(ls $metsfile > /dev/null 2> /dev/null); then
	    echo "Error: metsfile "$metsfile" not found, exiting.";
	    exit 1;
	else
	    echo "Using metsfile "$metsfile;
	fi
	vrtfile=`echo $xmlfile | perl -pe 's/\.xml/\.vrt/'`;
	echo "Generating "$vrtfile;
	# Remove lines with no word, i.e. an empty first field.
	# Such lines occur after numerals, e.g. "2 000 ihmistä".
	$convpy --mets $metsfile $xmlfile 2> /dev/null | perl -pe 'if (/^\t/) { $_="" }' > $vrtfile;
	echo "Validating result";
        if (ls --size $vrtfile | egrep '^0' > /dev/null 2> /dev/null); then
            echo "Warning: empty VRT file, renaming it to "$vrtfile".empty";
	    mv $vrtfile $vrtfile".empty";
            continue;
        fi
	if !($vrtvalidate $vrtfile); then
	    echo "Error: not valid VRT format, exiting.";
	    exit 1;
	fi
    fi
done
