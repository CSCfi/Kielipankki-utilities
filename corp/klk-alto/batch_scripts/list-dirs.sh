#!/bin/sh


if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo """
list-dirs.sh [DIR]

For each directory in DIR/*/*/alto, output its size in kilobytes,
total number of TextBlock elements in the XML files under it,
and its name, separated by tabs, in ascending size order.
"""
    exit 0;
fi

DIR=".";
if [ "$1" != "" ]; then
    if ! [ -d "$1" ]; then
	echo "No such directory: $1, exiting.";
    else
	DIR=$1;
    fi
fi

for dir in $DIR/*/*/alto*;
do
    kbytes=`du -c -k -d 0 $dir | tail -1 | cut -f1`;
    textblocks=`grep '<TextBlock ' $dir/*.xml | wc -l`;
    printf '%s\t%s\t%s\n' "$kbytes" "$dir" "$textblocks";
done | sort -n;
