#!/bin/sh

# How to generate VRTFILE and TSVFILE from a corpus (e.g. ethesis_en_ma_beh) on korp:
#
# VRTFILE: /v/korp/scripts/cwbdata2vrt-simple.sh -all --output-file ethesis_en_ma_beh.VRT ethesis_en_ma_beh
# TSVFILE: /v/util/cwb/utils/cwb-s-decode -r /v/corpora/registry -n ethesis_en_ma_beh -S text_pdfurl | /v/korp/scripts/vrt-convert-chars.py --decode > pdfurls
#          /v/util/cwb/utils/cwb-s-decode -r /v/corpora/registry -n ethesis_en_ma_beh -S text_date | /v/korp/scripts/vrt-convert-chars.py --decode > dates
#          paste pdfurls dates > ethesis_en_ma_beh_pdfurls_dates.tsv

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo """
get-text-and-metadata.sh CORPUSDIR TSVFILE VRTFILE TARGETDIR
  [--dry-run|--ignore-language|--skip-missing]

For each pdfurl and date given in TSVFILE, find the corresponding
text file (TXTFILE.txt) in directory CORPUSDIR and the line in
VRTFILE that contains the metadata for that text, i.e. the line
beginning with \"<text \". Copy TXTFILE.txt and the metadata line
(written to file TXTFILE.metadata) under TARGETDIR/CORPUSDIR/.

CORPUSDIR: The directory that contains the text files.
TSVFILE:   A file that contains the pdfurls and dates of the texts,
           each pdfurl and date on its own line separated by a tab.
VRTFILE:   A VRT file that has been generated from the text files.
TARGETDIR: The directory where files are copied.
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
targetdir=$4;
dry_run="false";
skip_missing="false";
ignore_language="false";

for arg in $@;
do
    if [ "$arg" = "--dry-run" ]; then
	dry_run="true";
    elif [ "$arg" = "--skip-missing" ]; then
	skip_missing="true";
    elif [ "$arg" = "--ignore-language" ]; then
	ignore_language="true";
    fi;
done

if [ "$dry_run" = "false" ]; then
    if ! [ -d "$targetdir" ]; then
	mkdir $targetdir;
    fi
    if ! [ -d "$targetdir/$corpusdir" ]; then
	mkdir $targetdir/$corpusdir;
    fi
fi

while read line
do
    found=0;
    txtfilename="";
    # English marked with "en"
    txtfilename_=`echo "$line" | ./pdfurl-date-to-txtfilename.pl "en"`;
    if [ "$txtfilename_" != "" ]; then
	if [ -f "$corpusdir/$txtfilename_" ]; then found=$((found + 1)); txtfilename=$txtfilename_; fi
    fi
    # English marked with "eng"
    txtfilename_=`echo "$line" | ./pdfurl-date-to-txtfilename.pl "eng"`;
    if [ "$txtfilename_" != "" ]; then
	if [ -f "$corpusdir/$txtfilename_" ]; then found=$((found + 1)); txtfilename=$txtfilename_; fi
    fi
    # Language not marked
    txtfilename_=`echo "$line" | ./pdfurl-date-to-txtfilename.pl ""`;
    if [ "$txtfilename_" != "" ]; then
	if [ -f "$corpusdir/$txtfilename_" ]; then found=$((found + 1)); txtfilename=$txtfilename_; fi
    fi
    # No date or language marked
    txtfilename_=`echo "$line" | ./pdfurl-to-txtfilename.pl`;
    if [ "$txtfilename_" != "" ]; then
	if [ -f "$corpusdir/$txtfilename_" ]; then found=$((found + 1)); txtfilename=$txtfilename_; fi
    fi

    if [ "$found" -gt "1" ]; then
	echo "Error: several txtfiles found for $line.";
	if [ "$dry_run" = "false" ]; then exit 1; fi;
    fi
    if [ "$found" -eq "0" ]; then
	# Try any language
	txtfilename_=`echo "$line" | ./pdfurl-date-to-txtfilename.pl "*"`;
	if [ "$txtfilename_" != "" ]; then
	    found=`ls $corpusdir/$txtfilename_ 2> /dev/null | wc -l`;
	    if [ "$found" -gt "1" ]; then
		echo "Error: several txtfiles found for $line.";
		if [ "$dry_run" = "false" ]; then exit 1; fi;
	    fi
	    if [ "$found" -eq "1" ]; then
		txtfilename=`ls $corpusdir/$txtfilename_ | cut -f2 -d'/'`;
		echo "Warning: txtfile found, but language is not English: $txtfilename";
		if [ "$dry_run" = "false" -a "$ignore_language" = "false" ]; then exit 1; fi;
	    else
		echo "Warning: txtfile not found for $line.";
		if [ "$dry_run" = "false" -a "$skip_missing" = "false" ]; then exit 1; fi;
	    fi
	else
	    echo "Warning: txtfile not found for $line.";
	    if [ "$dry_run" = "false" -a "$skip_missing" = "false" ]; then exit 1; fi;
	fi
    fi

    expr=`echo $line | cut -f1 -d' '`;
    metadatafile=`echo $txtfilename | perl -pe 's/\.txt/.metadata/;'`;
    metadatafile=$targetdir/$corpusdir/$metadatafile;
    if [ "$dry_run" = "true" ]; then
	metadatafile=/dev/null;
    fi
    if [ "$found" -eq "1" ]; then
	if ! (grep --fixed-strings $expr $vrtfile > $metadatafile); then
	    echo "Error: no metadata found for file $corpusdir/$txtfilename.";
	    if [ "$dry_run" = "false" ]; then exit 1; fi;
	fi
	if [ "$dry_run" = "false" ]; then
	    if ! (cp $corpusdir/$txtfilename $targetdir/$corpusdir/$txtfilename); then
		echo "Error: could not copy file $corpusdir/$txtfilename.";
		exit 1;
	    fi
	fi
    fi
    # start=`grep --line-number $expr $vrtfile | cut -f1 -d':'`;
    # lines=`tail -n +$start $vrtfile | egrep -m 1 --line-number '^</text>' | cut -f1 -d':'`;
    # echo $lines;

done < ${tsvfile};
