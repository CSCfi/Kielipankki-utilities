#!/bin/sh

for script in ./check-dependencies.sh \
		  ./extract-packages.sh \
		  ./copy-english-files.sh \
		  ./extract-metadata.sh \
		  ./combine-files.sh \
		  ./parse-files.sh \
		  ./split-files.sh \
		  ./conllu-to-vrt.sh;
do
    if !(ls $script > /dev/null 2> /dev/null); then
	echo "Script "$script" not found in the current directory";
	exit 1;
    fi
done

./check-dependencies.sh $1 && \
    ./extract-packages.sh $1 && \
    ./copy-english-files.sh $1 && \
    ./extract-metadata.sh $1 && \
    ./combine-files.sh $1 && \
    ./parse-files.sh $1 && \
    ./split-files.sh $1 && \
    ./conllu-to-vrt.sh $1;
