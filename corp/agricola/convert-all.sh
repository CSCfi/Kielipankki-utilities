#! /bin/bash

for SUB in $( ls xml ) ; do
    ./convert-subcorpus.sh xml/$SUB
done