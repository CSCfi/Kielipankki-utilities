#!/bin/sh

vrt_validate="vrt-validate";
if [ "$1" = "--vrtdir" ]; then
    vrtdir=$2;
    if ! (ls $vrtdir/$vrt_validate > /dev/null 2> /dev/null); then
	echo "Error: vrt-validate not found in "$vrtdir;
	exit 1;
    else
	vrt_validate=$vrtdir/vrt-validate;
    fi
else
    if ! (which $vrt_validate > /dev/null 2> /dev/null); then
	echo "vrt-validate not found, running with no VRT validation";
	echo "(define path to validator with --vrtdir VRTDIR)";
	vrt_validate="";
    fi
fi

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
	if [ "$vrt_validate" != "" ]; then
	    echo "validating "$vrtfile":";
	    $vrtdir/vrt-validate $vrtfile;
	fi
    fi
done

# Seems that sentence attributes 'id_sessions' and 'region' have always the same values in all sentences within a text.
# TODO: Move them as attributes of text?

# "|" is used in lemmas, so "#" is defined as compund boundary marker instead
# with option --compound-boundary-marker="#" of korp-make ("#" is not used in lemmas)
# TODO: should "|" be replaced with something else in lemmas?
