#!/bin/sh

# split the parsed files and process conllu files into vrt files
# TODO: the parser drops some comment lines out?
cd ethesis_en;
for dir in gradut vaitokset;
do
    cd $dir;
    subdirs="bio_ja_ymparistot elainlaaketiede farmasia humanistinen kayttaytymistiede laaketiede maajametsatiede matemaattis oikeustiede teologinen valtiotiede";
    if [ "$dir" = "gradut" ]; then
	subdirs="aleksanteri-instituutti "$subdirs;
    fi
    for subdir in $subdirs;
    do
	cd $subdir;
	cp ../../../split-conllu-files.pl .;
	for file in ALL*.CONLLU;
	do
	    # change filename info ("FILENAME_", newpar, sent_id and text comment lines) into "# FILENAME: ..."
	    # todo: renumber the sentences
	    # first two perl scripts combine FILENAMES that have been tokenized as two words
	    cat $file | perl -pe 's/FILENAME\t.*\n/FILENAME/;' | perl -pe 's/\tFILENAME2\t/\tFILENAME/;' | perl -pe 's/\n/¤/g;' | \
		perl -pe 's/# newpar¤# sent_id = [^¤]+¤# text = FILENAME_[^¤]+¤[^\t]+\tFILENAME_([^\t]+)\t[^¤]+¤/# FILENAME: \1¤/g;' | perl -pe 's/¤/\n/g;' | ./split-conllu-files.pl;
	done
	rm split-conllu-files.pl;
	cd ..;
    done
    cd ..;
done
cd ..;
