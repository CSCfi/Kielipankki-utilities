#! /bin/bash

for CDIR in $( ls -d las2/las2_* ) ; do
    ./convert-dir.sh $CDIR
done