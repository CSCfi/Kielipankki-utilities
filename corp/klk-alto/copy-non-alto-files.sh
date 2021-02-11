#!/bin/sh

dry_run="true";

for dir in $1/*/*/*/;
do
    n_metsfiles=0;
    moved_metsfiles=0;
    n_metsfiles=0;
    for metsfile in $dir/*_mets.xml;
    do
	n_metsfiles=$((n_metsfiles+1));
	xmlfiles=`echo $metsfile | perl -pe 's/_mets\.xml/_page-*.xml/;'`;
	n_xmlfiles=0;
	moved_xmlfiles=0;
	for xmlfile in $xmlfiles;
	do
	    n_xmlfiles=$((n_xmlfiles+1));
	    if (head -3 $xmlfile | grep '<root>' > /dev/null); then
		if [ "$dry_run" != "true" ]; then
		    cp --parents $xmlfile $2/;
		fi
		moved_xmlfiles=$((moved_xmlfiles+1));
	    fi 
	done
	if [ "$moved_xmlfiles" != "0" ]; then
	    if [ "$dry_run" != "true" ]; then
		cp --parents $metsfile $2/;
	    fi
	    moved_metsfiles=$((moved_metsfiles+1));
	    marker="";
	    if [ "$moved_xmlfiles" != "$n_xmlfiles" ]; then
		marker="<---";
	    fi
	    echo "$metsfile: moved xmlfiles: $moved_xmlfiles / $n_xmlfiles $marker";
	fi
    done
    if [ "$moved_metsfiles" != "0" ]; then
	marker="";
	if [ "$moved_metsfiles" != "$n_metsfiles" ]; then
	    marker="<---";
	fi	    
	echo "    $dir: moved metsfiles: $moved_metsfiles / $n_metsfiles $marker";
	echo "";
    fi
done
