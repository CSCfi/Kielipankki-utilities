#!/bin/sh

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo """
combine-dirs.sh THRESHOLD

Combine directories given in standard input into chunks smaller
than THRESHOLD kilobytes. If a directory is bigger than THRESHOLD,
make it a single chunk. 

The directories are given in standard input, each directory on its
own line containing: total size in kilobytes, name of directory,
and number of textblocks, separated by tabs, in ascending size order.

For each chunk, output a line with the total size of directories,
a tab, the list of directories separated by commas, a tab, and
the total number of textblocks.

"""
exit 0;
fi

total_size=0;
total_textblocks=0;
all_dirs="";
threshold=$1;

while read line
do
    size=`echo $line | perl -pe 's/ +/\t/g;' | cut -f1`;
    dir=`echo $line | perl -pe 's/ +/\t/g;' | cut -f2`;
    textblocks=`echo $line | perl -pe 's/ +/\t/g;' | cut -f3`;
    total_size=$((total_size+size))
    total_textblocks=$((total_textblocks+textblocks))
    # Total size is exceeded
    if [ "$total_size" -gt "$threshold" ]; then
	total_size=$((total_size-size))
	total_textblocks=$((total_textblocks-textblocks))
	# Print the previous dirs
	if [ "$all_dirs" != "" ]; then
	    printf '%s\t%s\t%s\n' "$total_size" "$all_dirs" "$total_textblocks";
	fi
	# and leave the current dir to the next batch job.
	all_dirs=$dir;
	total_size=$size;
	total_textblocks=$textblocks;
    else
	if [ "$all_dirs" = "" ]; then
	    all_dirs=$dir;
	else
	    all_dirs=$all_dirs","$dir;
	fi
    fi
done <&0;

if [ "$all_dirs" != "" ]; then
    printf '%s\t%s\t%s\n' "$total_size" "$all_dirs" "$total_textblocks";
fi
