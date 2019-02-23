#! /bin/bash

FIX_NESTED="perl bin/la_murre-add-clause-elems.pl --remove-cl"
XML_DIR=$1

mkdir vrt

for XML in $( ls $XML_DIR/*.xml | sed '/tausta/d' ) ; do
    CNAME=$( echo $XML | cut -f 2 -d '/' )
    VRT=$( echo $XML | sed 's|^las2/|vrt/|g' | sed 's/\.xml/\.vrt/g' )
    mkdir vrt/$CNAME
    bin/conv.py $XML $CNAME | $FIX_NESTED > $VRT
done
