#!/bin/sh

# get-textfilenames.sh CORPUSDIR TSVFILE
# E.g. get-textfilenames.sh ethesis_en_ma_beh ethesis_en_ma_beh_pdfurls_dates.tsv

for script in "pdfurl-date-to-txtfilename.pl" "pdfurl-to-txtfilename.pl";
do
    if !(ls $script > /dev/null 2> /dev/null); then
	echo "Script $script not found, exiting.";
	exit 1;
    fi
done

corpusdir=$1;
tsvfile=$2;

while read line
do
    echo "---";
    found=0;
    # English marked with "en"
    txtfilename=`echo "$line" | ./pdfurl-date-to-txtfilename.pl "en"`;
    if [ "$txtfilename" != "" ]; then
	if (ls $corpusdir/$txtfilename 2> /dev/null); then found=$((found + 1)); fi
    fi
    # English marked with "eng"
    txtfilename=`echo "$line" | ./pdfurl-date-to-txtfilename.pl "eng"`;
    if [ "$txtfilename" != "" ]; then
	if (ls $corpusdir/$txtfilename 2> /dev/null); then found=$((found + 1)); fi
    fi
    # Language not marked
    txtfilename=`echo "$line" | ./pdfurl-date-to-txtfilename.pl ""`;
    if [ "$txtfilename" != "" ]; then
	if (ls $corpusdir/$txtfilename 2> /dev/null); then found=$((found + 1)); fi
    fi
    # No date or language marked
    txtfilename=`echo "$line" | ./pdfurl-to-txtfilename.pl`;
    if [ "$txtfilename" != "" ]; then
	if (ls $corpusdir/$txtfilename 2> /dev/null); then found=$((found + 1)); fi
    fi

    if [ "$found" -gt "1" ]; then echo "Warning: ^^^ several txtfiles found for $line ^^^"; fi
    if [ "$found" -eq "0" ]; then
	# Try any language
	txtfilename=`echo "$line" | ./pdfurl-date-to-txtfilename.pl "*"`;
	if [ "$txtfilename" != "" ]; then
	    if (ls $corpusdir/$txtfilename 2> /dev/null); then
		echo "Warning: ^^^ txtfile(s) found, but language is not English ^^^";
	    else
		echo "Error: txtfile not found for $line";
	    fi
	else
	    echo "Error: txtfile not found for $line";
	fi
    fi

done < ${tsvfile};
