#!/bin/sh

# ./divide-by-language.sh LANGUAGE TARGETDIR

lang=$1;
targetdir=$2;

for upperdir in klk_1.1.2014-30.6.2014_vrt/*/;
do
    for dir in $upperdir/*/alto;
    do
	rm -f tmp;
	touch tmp;
	for metsfile in $dir/*mets.xml;
	do
	    cat $metsfile | egrep -m 1 '<MODS\:languageTerm' | cut -f2 -d'>' | cut -f1 -d'<' >> tmp;
	done;
	cat tmp | sort | uniq > TMP;
	nlanguage=`cat TMP | wc -l`;
	language=`cat TMP`;
	rm -f TMP;
	if [ "$language" = "$lang" ]; then
	    echo "Copying all VRT files from directory "$dir".";
	    cp --parents $dir/*.vrt $targetdir/;
	else
	    if [ "$nlanguage" -gt "1" ]; then
		echo "More than one language in directory "$dir", copying VRT files one by one.";
		for vrtfile in $dir/*.vrt;
		do
		    if (cat $vrtfile | grep -m 1 ' language="'$lang'"' > /dev/null); then
			echo "  Copying VRT file "$vrtfile".";
			cp --parents $vrtfile $targetdir/;
		    fi
		done;
	    fi
	fi
    done;
done
