#!/bin/sh


if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo """
For each directory in */*/alto, output its size in kilobytes
and name, separated by a tab, in ascending order.
"""
    exit 0;
fi

for dir in */*/alto*;
do
    kbytes=`du -c -k -d 0 $dir/*.xml | tail -1 | cut -f1`;
    echo $kbytes"\t"$dir;
done | sort -n;
