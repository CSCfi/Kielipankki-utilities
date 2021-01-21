#!/bin/sh

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo """
dirs-into-game-commands.sh GAMESCRIPT ALTOSCRIPT THRESHOLD1 THRESHOLD2

Generate batch job commands based on input from standard in
that contains parameters for each batch job on a separate line
in the following format:

size   dir1,dir2, ... ,dirN   textblocks

where size is total size of directories dir1 from dirN, in kilobytes,
and textblocks is total number of TextBlock elements.
The corresponding command generated will be:

  GAMESCRIPT --hours=HOURS ALTOSCRIPT dir1 dir2 ... dirN

where

  GAMESCRIPT is full path to game script
  HOURS is time reserved for the script, in hours, defined as
        max(size/THRESHOLD1 + 1, textblocks/THRESHOLD2 + 1)
  ALTOSCRIPT is full path to the alto-to-vrt script
"""
    exit 0;
fi

gamescript=$1
altoscript=$2;
size_threshold=$3;
block_threshold=$4;

while read line;
do
    size=`echo $line | perl -pe 's/ +/\t/g;' | cut -f1`;
    hours=$(($size/$size_threshold+1));
    dirs=`echo $line | perl -pe 's/ +/\t/g;' | cut -f2 | perl -pe 's/,/ /g;'`;
    textblocks=`echo $line | perl -pe 's/ +/\t/g;' | cut -f3`;
    if [ "$block_threshold" != "" ]; then
	hours_blocks=$(($textblocks/$block_threshold+1));
	if [ "$hours_blocks" -gt "$hours" ]; then
	    hours=$hours_blocks;
	fi
    fi
    echo $gamescript "--hours="$hours $altoscript '"'$dirs'"';
done <&0;
