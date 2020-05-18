#!/bin/sh

# How to generate VRTFILE and TSVFILE from a corpus (e.g. ethesis_en_ma_beh) on korp:
#
# VRTFILE: /v/korp/scripts/cwbdata2vrt-simple.sh -all --output-file ethesis_en_ma_beh.VRT ethesis_en_ma_beh
# TSVFILE: /v/util/cwb/utils/cwb-s-decode -r /v/corpora/registry -n ethesis_en_ma_beh -S text_pdfurl | /v/korp/scripts/vrt-convert-chars.py --decode > pdfurls
#          /v/util/cwb/utils/cwb-s-decode -r /v/corpora/registry -n ethesis_en_ma_beh -S text_date | /v/korp/scripts/vrt-convert-chars.py --decode > dates
#          paste pdfurls dates > ethesis_en_ma_beh_pdfurls_dates.tsv

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo """
get-txtfilenames.sh CORPUSDIR TSVFILE [VRTFILE]

For each pdfurl and date given in TSVFILE, find the corresponding
text file in directory CORPUSDIR. If VRTFILE is given, print the
number of lines for the text in that file.

CORPUSDIR: The directory that contains the text files.
TSVFILE:   A file that contains the pdfurls and dates of the texts,
           each pdfurl and date on its own line separated by a tab.
VRTFILE:   A VRT file that has been generated from the text files.
    """
    exit 0;
fi

for script in "pdfurl-date-to-txtfilename.pl" "pdfurl-to-txtfilename.pl";
do
    if !(ls $script > /dev/null 2> /dev/null); then
	echo "Script $script not found, exiting.";
	exit 1;
    fi
done

corpusdir=$1;
tsvfile=$2;
vrtfile=$3;

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
		found=$((found + 1));
	    else
		echo "Error: txtfile not found for $line";
	    fi
	else
	    echo "Error: txtfile not found for $line";
	fi
    fi

    # How many lines there are in the VRT file
    if [ "$vrtfile" != "" -a  "$found" -gt "0" ]; then
	expr=`echo $line | cut -f1 -d' '`;
	start=`grep --line-number $expr $vrtfile | cut -f1 -d':'`;
	metadataline=`grep $expr $vrtfile`;
	lines=`tail -n +$start $vrtfile | egrep -m 1 --line-number '^</text>' | cut -f1 -d':'`;
	# echo $lines;
	echo $metadataline;
    fi

done < ${tsvfile};
