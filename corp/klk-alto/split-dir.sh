#!/bin/sh

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo ""
    echo "split-dir.sh DIR THRESHOLD [--dry-run]"
    echo ""
    echo "Split directory DIR into directories smaller than THRESHOLD kilobytes."
    echo "The new directories will be named alto_1, alto_2, ... and the original"
    echo "renamed to orig_alto."
    echo ""
    echo "Size of directory is defined based on *.xml files."
    echo ""
    exit 0;
fi

threshold=$2;
subdir_N=1;
subdir_prefix="alto_";
dry_run="false";
if [ "$3" = "--dry-run" ]; then
    dry_run="true";
fi

# total size of directory
kbytes=`du -c -k -d 0 $1 | tail -1 | cut -f1`;
if ! [ "$kbytes" -gt "$threshold" ]; then
    echo "No need to split directory";
    exit 0;
fi

kbytes=0;
subdir=$1"/../"$subdir_prefix$subdir_N"/";
echo "Copying to directory $subdir";
if ! [ -d "$subdir" ]; then
    if [ "$dry_run" != "true" ]; then mkdir $subdir; fi;
fi

for metsfile in $1/*_mets.xml;
do
    # process all xml files that use the current mets file
    xmlfiles=`echo $metsfile | perl -pe 's/_mets\.xml/_page-*.xml/;'`
    more_kbytes=`du -c -k -d 0 $xmlfiles $metsfile | tail -1 | cut -f1`;
    kbytes=$((kbytes+more_kbytes));

    if [ "$kbytes" -gt "$threshold" ]; then
	subdir_N=$((subdir_N+1));
	subdir=$1"/../"$subdir_prefix$subdir_N"/";
	echo "Copying to directory $subdir";
	if ! [ -d "$subdir" ]; then
	    if [ "$dry_run" != "true" ]; then mkdir $subdir; fi;
	fi
	kbytes=$more_kbytes;
    fi

    if [ "$dry_run" != "true" ]; then
	cp $metsfile $subdir;
	for xmlfile in $xmlfiles;
	do
	    cp $xmlfile $subdir;
	done
    fi

done

orig_alto=`echo $1 | perl -pe 's/\/alto/\/orig_alto/;'`;
echo "Renaming $1 to $orig_alto";
if [ "$dry_run" != "true" ]; then
    mv $1 $orig_alto;
fi
