#!/bin/bash

# vrtvalidate="";

for lang in koi kpv krl mdf myv olo udm;
do
    if !(ls $lang > /dev/null); then
	exit 1;
    fi
    cd $lang;
    if !(ls ${lang}-${number}*.vrt > /dev/null); then
	exit 1;
    fi
    files=`ls ${lang}-${number}*.vrt`;
    for file in $files;
    do
	echo $file;
	# - remove U+FEFF
	# - separate each tag to its own line
	# - rename text attribute that contains numerals
	# - fix suspect date
	# - add link tags
	cat $file | perl -C -pe 's/\x{feff}//;' | perl -pe 's/></>\n</g;' | \
	    perl -pe 'if (/^<text/) { s/iso_639="/iso_lang="/; s/datefrom="200801010"/datefrom="20080101"/; }' | \
	    perl -pe 's/^(<sentence id="([^"]*)")/<link id="\2">\n\1/;' | perl -pe 's/^(<\/sentence>)/\1\n<\/link>/;' > $file.tmp;
	# $vrtvalidate $file.tmp;
    done
    cd ..;
done
