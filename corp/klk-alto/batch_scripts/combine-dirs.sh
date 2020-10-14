#!/bin/sh

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo """
combine-dirs.sh THRESHOLD

Combine directories given in standard input into chunks smaller
than THRESHOLD kilobytes. If a directory is bigger than THRESHOLD,
make it a single chunk. 

The directories are given in standard input, each directory on its
own line containing: total size in kilobytes and name, separated
by a tab, in ascending order.

For each chunk, output a line with the total size of directories,
a tab, and the list of directories, separated by spaces.

"""
exit 0;
fi

total_size=0;
all_dirs="";
threshold=$1;

while read line
do
    size=`echo $line | perl -pe 's/ +/\t/;' | cut -f1`;
    dir=`echo $line | perl -pe 's/ +/\t/;' | cut -f2`;
    total_size=$((total_size+size))
    # Total size is exceeded
    if [ "$total_size" -gt "$threshold" ]; then
	total_size=$((total_size-size))
	# Print the previous dirs
	if [ "$all_dirs" != "" ]; then
	    echo -e $total_size"\t"$all_dirs;
	fi
	# and leave the current dir to the next batch job.
	all_dirs=$dir;
	total_size=$size;
    else
	if [ "$all_dirs" = "" ]; then
	    all_dirs=$dir;
	else
	    all_dirs=$all_dirs" "$dir;
	fi
    fi
done <&0;

if [ "$all_dirs" != "" ]; then
    echo -e $total_size"\t"$all_dirs;
fi
