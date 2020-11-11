#!/bin/sh

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo """
change-language.sh DIR LANG1 LANG2

Change text attribute 'language' from LANG1 to LANG2 in all
VRT files LANG1/DIR/*/*/*.vrt and copy the VRT files to
LANG2/DIR/.

If LANG2/DIR/ does not exist, it is created. Full pathnames
are preserved, i.e. 'LANG1/DIR/foo/bar/baz.vrt' is copied to
'LANG2/DIR/foo/bar/baz.vrt'.
    """;
    exit 0;
fi

DIR=`pwd`;

dir=$1;
old_lang=$2;
new_lang=$3;

old_dir="$old_lang/$dir";
new_dir="$new_lang/$dir";

if ! [ -d "$old_dir" ]; then
    echo "Error: no such directory: $old_dir, exiting";
    exit 1;
fi
if ! [ -d "$new_dir" ]; then
    echo "Creating directory $new_dir";
    mkdir $new_dir;
fi

cd $old_dir;
for subdir in */;
do
    echo "Checking if "$old_dir/$subdir" can be copied as "$new_dir/$subdir;
    if [ -d $new_dir/$sudbdir ]; then
	echo "Error: directory $new_dir/$subdir already exists, exiting";
	cd $DIR;
	exit 1;
    fi
done
cd $DIR;

echo "Changing value of each attribute 'language' in all vrt files";
for file in $old_dir/*/*/*.vrt;
do
    # echo "Changing value of each attribute 'language' in file $file";
    cat $file | perl -pe 'if (/^<text /) { s/ language="'$old_lang'"/ language="'$new_lang'"/; }' > tmp;
    mv tmp $file;
done

echo "Copying "$old_dir/*" under "$new_dir;
cp -r $old_dir/* $new_dir/;
