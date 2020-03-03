#!/bin/bash


book_numbers=$(seq 41 67);
for number in $book_numbers;
do
    for lang in koi kpv krl mdf myv olo udm fin;
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
	    bundled=`grep 'id="' $file | egrep '[0-9]\-[0-9]' | perl -pe 's/.* id="([^"]*)".*/\1/;'`;
	    if [ "${#bundled}" != "0" ]; then
		for id in `echo $bundled`;
		do
		    echo $id" "$lang;
		done
	    fi
	done
	cd ..;
    done;
    echo "";
done
