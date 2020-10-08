#!/bin/sh

if [ "$1" = "-h" -o "$1" = "--help" ]; then
echo """
text-and-metadata-to-tnpp.sh SOURCEDIR LIMIT

For each *.txt and corresponding *.metadata file in SOURCEDIR,
append the metadata (inside comments) and text to file
SOURCEDIR/TEXT_N.TXT where N is defined as (n / LIMIT + 1),
when nth file is being processed.
"""
exit 0;
fi

sourcedir=$1;
limit=$2;
nfiles=0;
prefix="TEXT_";
number=1;
extension=".TXT";
first_text="false";

if ! [ -f "fix-special-characters.pl" ]; then
    echo "Script fix-special-characters.pl not found, exiting.";
    exit 1;
fi

for sourcefile in $sourcedir/*.txt;
do
    metadatafile=`echo $sourcefile | perl -pe 's/\.txt/.metadata/;'`;
    if ! [ -f "$metadatafile" ]; then
	echo "Error: file "$metadatafile" does not exist, exiting.";
	exit 1;
    fi
    number=$((nfiles / limit + 1));
    targetfile=$sourcedir/$prefix$number$extension;
    if ! [ -f "$targetfile" ]; then
	touch $targetfile;
	first_text="true";
    fi
    echo "Writing "$sourcefile" to file "$targetfile"...";
    nfiles=$((nfiles + 1));
    # If this is not the first <text>, append </text> to the previous <text>.
    # Note that the last <text> will intentionally miss </text>
    # as TNPP cannot have a comment line at the end of input.
    # The missing </text> is later appended in script conllu-to-vrt.pl.
    if [ "$first_text" = "false" ]; then
	echo "" >> $targetfile;
	echo "" >> $targetfile;
	echo "###C: </text>" >> $targetfile;
    fi
    echo "###C: " | tr -d '\n' >> $targetfile;
    cat $metadatafile | ./fix-special-characters.pl >> $targetfile;
    echo "" >> $targetfile;
    cat $sourcefile | ./fix-special-characters.pl | perl -pe 's/<BR>/\n/g;' | perl -pe 's/ +/ /g;' >> $targetfile;
    first_text="false";
done