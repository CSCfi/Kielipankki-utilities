#!/bin/sh

path=""
xmlfile=""
vrtfile=""
tmpfiles="false"

for arg in "$@"
do
    if [ "$arg" = "--script-path" ]; then
	path="next...";
    elif [ "$arg" = "--vrt-file" ]; then
	vrtfile="next...";
    elif [ "$path" = "next..." ]; then
	path=$arg;
    elif [ "$vrtfile" = "next..." ]; then
	vrtfile=$arg;
    elif [ "$arg" = "--help" -o "$arg" = "-h" ]; then
	echo "Usage: "$0" XMLFILE [--script-path PATH] [--vrt-file VRTFILE]";
	exit 0;
    elif [ "$arg" = "--tmp-files" ]; then
	tmpfiles="true";
    elif [ "$xmlfile" = "" ];then
	xmlfile=$arg;
    else
	echo "Option not recognized: "$arg;
	echo "Usage: "$0" XMLFILE [--script-path PATH] [--vrt-file VRTFILE]";
	exit 1;
    fi
done

if [ "$xmlfile" = "" ]; then
    echo "ERROR: name of xml file must be given"; exit 1;
fi
if !(ls $xmlfile > /dev/null 2> /dev/null); then
    echo "ERROR: no such file: "$xmlfile; exit 1;
fi
if [ "$vrtfile" = "" ]; then
    vrtfile=`echo $xmlfile | perl -pe 's/\.xml/\.vrt/'`
fi
link_prefix=`echo $xmlfile | perl -pe 's/\.xml//'`

if [ "$tmpfiles" = "true" ]; then
    cat $xmlfile | $path/move-johtolause.pl > tmp1
    cat tmp1 | $path/insert-paragraphs.pl > tmp2
    cat tmp2 | $path/separate-xml-tags.pl > tmp3
    cat tmp3 | $path/trim.pl > tmp4
    cat tmp4 | $path/mark-doc-parts.pl > tmp5
    cat tmp5 | $path/mark-heading-paragraphs.pl > tmp6
    cat tmp6 | $path/insert-vrt-tags.pl > tmp7
    cat tmp7 | $path/process-identifiointiosa.pl > tmp8
    cat tmp8 | $path/process-allekirjoitusosa.pl > tmp9
    cat tmp9 | $path/process-liiteosat.pl > tmp10
    cat tmp10 | $path/process-saadososa.pl > tmp11
    cat tmp11 | $path/remove-orig-xml-tags.pl > tmp12
    cat tmp12 | $path/check-paragraphs.pl > tmp13
    cat tmp13 | $path/check-sections.pl > tmp14
    cat tmp14 | $path/move-titles.pl > tmp15
    cat tmp15 | $path/tokenize.pl > tmp16
    cat tmp16 | $path/insert-sentence-tags.pl --filename $xmlfile --limit 150 > tmp17
    cat tmp17 | $path/insert-links.pl --link-prefix $link_prefix > tmp
else
    cat $xmlfile | \
	$path/move-johtolause.pl | \
	$path/insert-paragraphs.pl | \
	$path/separate-xml-tags.pl | \
	$path/trim.pl | \
	$path/mark-doc-parts.pl | \
	$path/mark-heading-paragraphs.pl | \
	$path/insert-vrt-tags.pl | \
	$path/process-identifiointiosa.pl | \
	$path/process-allekirjoitusosa.pl | \
	$path/remove-orig-xml-tags.pl | \
	$path/check-paragraphs.pl | \
	$path/check-sections.pl | \
	$path/move-titles.pl | \
	$path/tokenize.pl | \
	$path/insert-sentence-tags.pl --filename $xmlfile --limit 150 | \
	$path/insert-links.pl --link-prefix $link_prefix > tmp
fi

doctype=`cat $xmlfile | $path/get-doc-type.pl`

url_year=`echo $xmlfile | perl -pe 's/.*asd([0-9][0-9][0-9][0-9]).*/\1/g;'`
url_number=`echo $xmlfile | perl -pe 's/\.xml//g; s/asd\/(fi|sv)\/[0-9][0-9][0-9][0-9]\///g; s/(s|t)$//g; s/asd[0-9][0-9][0-9][0-9]//g; s/^0+//g;'`
url_lang=`echo $xmlfile | perl -pe 's/asd\/(fi|sv).*/\1/'`

url=""
# if statute number is too long, leave the url field empty
length=`printf "%s" "$url_number" | wc -c`
if [ "$length" -gt 4 ]; then
    url="";
else
    url="http://data.finlex.fi/eli/sd/"$url_year"/"$url_number"/alkup/"$url_lang".html"
fi

datefrom=$url_year"0101"
dateto=$url_year"1231"

echo '<text filename="'$xmlfile'" datefrom="'$datefrom'" dateto="'$dateto'" timefrom="000000" timeto="235959" url="'$url'" type="'$doctype'">' > $vrtfile
cat tmp >> $vrtfile
echo '</text>' >> $vrtfile
