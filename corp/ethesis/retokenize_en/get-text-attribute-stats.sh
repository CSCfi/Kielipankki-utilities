#!/bin/sh

inputfile=$1;
threshold="0";
if [ "$2" != "" ]; then
    threshold=$2;
fi

echo "";
printf "%-20s\t%-10s\t%s\t%s\n" ATTRIBUTE "DEFINED (EMPTY)" VALUES "(VALUE SET)";
echo "";

lines=`wc -l $1 | cut -f1 -d' '`;

for attribute in citation_language citation_authors url keywords citation_pdf_url date title faculty faculty_directory subject type datefrom dateto;
do
    hits=`grep -c $attribute'="' $1`;
    grep $attribute'="' $inputfile | perl -pe 's/^.* '$attribute'="([^"]*)".*$/\1/;' | sort | uniq -c | sort -nr > tmp;
    # empty values
    emptyn=`egrep '_$' tmp | perl -pe 's/^[^0-9]+([0-9]+)[^0-9]*/\1/;'`;
    nvalues=`wc -l tmp | cut -f1 -d' '`;
    printf "%-20s\t%-10s\t%s\n" $attribute $hits" ("$emptyn")" $nvalues;
    if [ "$nvalues" -lt "$threshold" ]; then
	# valuesstr=`cat tmp | perl -pe 's/^.{8}//; s/\n/", "/;' | perl -pe 's/^/("/; s/, "$/)/;'`;
	cat tmp | perl -pe 's/^/\t\t\t\t\t\t/;';
    fi
    rm tmp;
done

echo "";
printf "%-20s\t%-10s\t%s\n" "LINES IN TOTAL" $lines;
echo "";
