#!/bin/sh

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo """
dirs-into-game-commands.sh GAMESCRIPT ALTOSCRIPT THRESHOLD

Generate batch job commands based on input from standard in
that contains parameters for each batch job on a separate line
in the following format:

size   dir1 dir2 ... dirN

where size is total size of directories dir1 from dirN, in kilobytes.
The corresponding command generated will be:

  GAMESCRIPT --hours=HOURS ALTOSCRIPT dir1 dir2 ... dirN

where

  GAMESCRIPT is full path to game script
  HOURS is time reserved for the script, in hours (size / THRESHOLD + 1)
  ALTOSCRIPT is full path to the alto-to-vrt script
"""
    exit 0;
fi

gamescript=$1
altoscript=$2;
threshold=$3;

while read line;
do
    size=`echo $line | perl -pe 's/ +/\t/;' | cut -f1`;
    hours=$(($size/$threshold+1));
    dirs=`echo $line | perl -pe 's/ +/\t/;' | cut -f2`;
    echo $gamescript "--hours="$hours $altoscript '"'$dirs'"';
done <&0;
