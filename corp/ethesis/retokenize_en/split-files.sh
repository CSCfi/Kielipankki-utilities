#!/bin/sh

# split the parsed files and process conllu files into vrt files
# TODO: the parser drops some comment lines out?

verbose="false";
for arg in $@;
do
    if [ "$arg" = "--verbose" ]; then
	verbose="true";
    fi
done

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
	if [ "$verbose" = "true" ]; then
	    echo "Splitting files in "$dir"/"$subdir;
	fi
	cp ../../../split-conllu-files.pl .;
	for file in ALL*.CONLLU;
	do
	    # change filename info ("FILENAME_", newpar, sent_id) into "# FILENAME: ..."
	    # todo: renumber the sentences
	    cat $file | perl -pe 's/\n/¤/g;' | perl -pe 's/# newpar¤# sent_id = [^¤]+¤# text = "FILENAME_([^"]+)"/# FILENAME: \1/g;' | perl -pe 's/¤/\n/g;' > tmp;
	    filenames=`cat tmp | egrep '^# FILENAME' | perl -pe 's/# FILENAME\: //;'`;
	    for filename in $filenames;
	    do
		if !(ls $filename > /dev/null 2> /dev/null); then
		    echo "Warning: no such source file: "$dir"/"$subdir"/"$filename;
		fi
	    done
	    cat tmp | ./split-conllu-files.pl;
	    rm tmp;
	done
	rm split-conllu-files.pl;
	cd ..;
    done
    cd ..;
done
cd ..;
