#! /bin/bash

SUB_DIR=$1
FIX_NESTED="perl bin/la_murre-add-clause-elems.pl --remove-cl"

for XML in $( ls $SUB_DIR/*.xml ) ; do
    SUB=$( echo $SUB_DIR | cut -f 2 -d '/' )
    VRT=$( echo $XML | sed 's/xml/vrt/g' )
    bin/conv.py $XML $SUB | $FIX_NESTED > $VRT
done