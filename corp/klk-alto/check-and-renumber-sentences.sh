#!/bin/sh

vrt_validate="vrt-validate";
if ! [ -d "$1" ]; then
    echo "Error: no such directory: $1, exiting.";
    exit 1;
fi
if ! (which $vrt_validate > /dev/null); then
    echo "Error: $vrt_validate not found, exiting.";
    exit 1;
fi

for file in $1/*/*/*/*.vrt;
do
    echo $file;
    if (egrep '^<sentence>' $file > /dev/null 2> /dev/null); then
	newfile=`echo $file | perl -pe 's/\.vrt$/\.vrt\.renumbered/;'`;
	echo "renumbering sentences in $file";
	# rewrite <sentence... as <sentence id="ID">, where ID
	# is consecutive number, beginning from 0 for each new <text>
	cat $file | perl -pe 'if (/^<text/) { ${id}=-1; }; if (/^<sentence/) { $_ = "<sentence id=\"".++${id}."\">\n"; }' > $newfile;
	if ($vrt_validate $newfile); then
	    mv $newfile $file;
	else
	    echo "Error when validating $newfile, exiting.";
	    exit 1;
	fi
    fi 
done
