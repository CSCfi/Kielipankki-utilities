#!/bin/sh
cd ethesis_en;
for dir in $1;
do
    if ! (ls $dir > /dev/null 2> /dev/null); then
	echo "No such directory: "$dir;
	continue;
    fi
    echo "---------- "$dir" ----------";
    cd $dir;
    for subdir in $2;
    do
	if ! (ls $subdir > /dev/null 2> /dev/null); then
	    echo "(No such subdirectory: "$subdir")";
	    continue;
	fi
	cd $subdir;
	echo "";
	echo $subdir":";
	echo "";
	txtfiles=$3;
	if [ "$txtfiles" = "" ]; then
	    txtfiles="ALL*.TXT";
	fi
	for file in $txtfiles;
	do
	    if ! (ls $file > /dev/null 2> /dev/null); then
		echo "(No such file: "$file")";
	    else
		echo $file | perl -pe 's/\n/:\t/;';
		cat $file | egrep '^###C: FILENAME:' | uniq | wc -l;
	    fi
	done;
	echo "--" ;
	conllufiles=$4;
	if [ "$conllufiles" = "" ]; then
	    conllufiles="ALL*.CONLLU";
	fi
	for file in $conllufiles;
	do
	    if ! (ls $file > /dev/null 2> /dev/null); then
		echo "(No such file: "$file")";
	    else
		echo $file | perl -pe 's/\n/:\t/;';
		cat $file | egrep '^# FILENAME:' | uniq | wc -l;
	    fi
	done;
	cd ..;
	echo "";
	echo "-----";
	echo "";
    done;
    cd ..;
done
