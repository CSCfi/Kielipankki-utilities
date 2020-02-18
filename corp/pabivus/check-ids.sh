#!/bin/bash

allow_bundled="false";
book_numbers=$(seq 41 67);
brief_diff="false";

for arg in $@;
do
    if [ "$book_numbers" = "<next>" ]; then
	book_numbers=$arg;
    else
	if [ "$arg" = "--allow-bundled" ]; then
	    allow_bundled="true";
	fi
	if [ "$arg" = "--brief-diff" ]; then
	    brief_diff="true";
	fi
	if [ "$arg" = "--book-numbers" ]; then
	    book_numbers="<next>";
	fi
	if [ "$arg" = "--help" -o "$arg" = "-h" ]; then
	    echo "Usage: check-ids.sh [--allow-bundled] [--brief-diff] [--book-numbers NUMBERS]"
	    echo "VRT files must follow pattern LANG/LANG-BOOKNUMBER_BOOKID-YEAR_vrt.vrt, e.g."
	    echo "\"myv/myv-48_2CO-2006_vrt.vrt\".";
	    exit 0;
	fi
    fi
done

diff="diff";
if [ "$brief_diff" = "true" ]; then
    diff="diff --brief";
fi

echo "";
echo "book/lang       koi     kpv     krl     mdf     myv     olo     udm";
echo "";
for number in $book_numbers;
do
    echo $number | perl -pe 's/\n/\t\t/;';
    DIFF="false";
    HITS="";
    versions="";
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
	    versions=$versions$lang"/"$file".uniquedids ";
	    rm -f $file.uniquedids;
	    touch $file.uniquedids;
	    if [ "$allow_bundled" = "true" ]; then
		# e.g. "b.MRK.14.51–52" -> "b.MRK.14.51" "b.MRK.14.52"
		ids=`egrep '^<sentence id="' $file | perl -pe 's/<sentence id="([^"]+)".*/\1/;'`;
		for id in $ids;
		do
		    modified=`echo $id | perl -pe 's/—/-/g;' | perl -pe 's/(b\.[^.]+\.[^.]+\.)([0-9]+)-([0-9]+)/for i in \\\$\(seq \2 \3\)\; do echo \1\\\$i\; done/;'`;
		    if (echo ${modified} | egrep '^for' > /dev/null); then
			echo ${modified} | sh >> $file.uniquedids;
		    else
			echo ${modified} >> $file.uniquedids;
		    fi
		done
	    else
		egrep '^<sentence id="' $file | perl -pe 's/<sentence id="([^"]+)".*/\1/;' >> $file.uniquedids;
	    fi
	    hits=`wc -l $file.uniquedids | cut -f1 -d' '`;
	    if [ "$HITS" = "" ]; then
		HITS=$hits;
	    fi
	    if [ "$hits" != "$HITS" ]; then
		DIFF="true";
	    fi
	    HITS=$hits;
	    echo $hits | perl -pe 's/\n/,/;';
	done
	cd ..;
	echo "" | perl -pe 's/\n/\t/;';
    done;
    if [ "$DIFF" = "true" ]; then
	echo "" | perl -pe 's/\n/\t/;';
	echo "<--" | perl -pe 's/\n//;';
    fi
    echo "";
    for version1 in $versions;
    do
	for version2 in $versions;
	do
	    if [[ "$version1" < "$version2" ]]; then
		diff_output=`$diff $version1 $version2`;
		if [ "$diff_output" != "" ]; then
		    echo "diff "$version1" "$version2":";
		    echo $diff_output | perl -pe 's/([^ ]+ [<>] [^ ]+ )/\1\n/g;';
		fi
	    fi
	done
    done
done
