#!/bin/sh

threshold=0;
if [ "$2" != "" ]; then
    threshold=$2;
fi

for attribute in birth_decade end gender id_session id_utterance participant region start;
do
    cat $1 | egrep '^<sentence ' | perl -pe 's/^.* '$attribute'="([^"]*)".*$/\1/;' | sort | uniq -c | sort -nr > tmp;
    nvalues=`cat tmp | wc -l`;
    echo $attribute"\t"$nvalues;
    if [ "$nvalues" -lt "$threshold" ]; then
	cat tmp;
    fi
    rm tmp;
done
