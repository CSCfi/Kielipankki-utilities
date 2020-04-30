#!/bin/sh

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo "";
    echo "generate-game-commands.sh GAMESCRIPT ALTOSCRIPT";
    echo "";
    echo "For all directories DIR in */*/alto (given as input), generate a command:";
    echo "";
    echo "  GAMESCRIPT --hours=HOURS ALTOSCRIPT DIRS"
    echo "";
    echo "where HOURS is number of requested hours based on the size of the directories."
    echo "";
    exit 0;
fi

gamescript=$1
altoscript=$2;
size=0;

while read line;
do
    hours=1;
    mbytes=`du -c -m -d 0 $dir/*.xml | tail -1 | cut -f1`;
    for threshold in 100 200 300 400 500 600 700 800 900 1000;
    do
	if [ "$mbytes" -gt "$threshold" ]; then
	    hours=$((hours + 1));
	fi
    done
    echo $gamescript "--hours="$hours $altoscript $dir;
done <&0;
