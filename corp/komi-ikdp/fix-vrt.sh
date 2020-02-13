#!/bin/sh

for file in *.vrt.txt;
do
    if (wc -l $file | egrep '^0 ' > /dev/null); then
	echo "skipping empty file "$file;
    else
	# input *.vrt.txt, output *.vrt
	vrtfile=`echo $file | perl -pe 's/\.vrt\.txt/\.vrt/;'`;
	# declare positional attributes
	echo "<!-- #vrt-positional-attributes: word ref lemma msd -->" > $vrtfile;
	# - tags to their own lines
	# - fix wrong number of fields (caused by reduplication?)
	# - add missing newline to end of file
	# - add text attribute corpus_shortname
	# - swap first and second fields ( ref word -> word ref )
	# - add missing third and fourth fields with empty values ( foo 1 -> foo 1 _ _ )
	cat $file | perl -pe 's/></>\n</g;' | perl -C -pe 's/(\t\|)\t/\1/g; s/\|\t"/|"/g;' | perl -pe 's/<\/text>/<\/text>\n/;' | perl -pe 's/^\n$//;' | perl -pe 'if (/^<text/) { s/<text/<text corpus_shortname="komi-ikdp"/; }' | perl -pe 'unless (/^</) { s/^([^\t]+)\t([^\t\n]+)/\2\t\1/; }' | perl -pe 'unless (/^</) { s/^([^\t]+\t[^\t]+)\n$/\1\t_\t_\n/; }' >> $vrtfile;
	echo "validating "$vrtfile":";
	$vrttools/vrt-validate $vrtfile;
    fi
done
