#!/bin/sh

source venv-parser-neural/bin/activate;
for file in ethesis_en/*/*/ALL*.TXT; do
    if [ "$1" = "--verbose" ]; then
	echo "Parsing "$file;
    fi
    cat $file | perl -pe 's/^/\n/;' | python3 full_pipeline_stream.py --gpu -1 --conf models_en_ewt/pipelines.yaml parse_plaintext 2> /dev/null > `echo $file | perl -pe 's/(ALL[0-9]+)\.TXT/\1.CONLLU/;'`;
done
deactivate;
