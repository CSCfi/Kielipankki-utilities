#!/bin/sh

verbose="false";
for arg in $@;
do
    if [ "$arg" = "--verbose" ]; then
	verbose="true";
    fi
done

# get metadata
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
	if [ "$verbose" = "true" ]; then echo "Grepping metadata for "$dir"/"$subdir; fi
	cd $subdir;
	# touch GREP;
	metadatafile="metadata_txt";
	if [ "$dir" = "gradut" -a '(' "$subdir" = "maajametsatiede" -o "$subdir" = "matemaattis" -o "$subdir" = "valtiotiede" ')' ]; then
	    metadatafile="metadata_vrt";
	fi
	for file in *.txt;
	do
	    echo $file | perl -pe 's/(_DATE=[0-9]{4}(\-[0-9]{2})?(\-[0-9]{2})?)?\.txt/\\.pdf/; s/^(.*)$/grep "\/\1" '$metadatafile'/;' | sh | perl -pe 's/^[^<]*(<text[^>]+>).*$/\1/;' | egrep '(citation_)?lang(uage)?="(eng?)?"' | sort | uniq > hits;
	    cp hits $file.hits;
	    hits=`wc -l hits | perl -pe 's/^([0-9]+).*$/\1/;'`;
	    orig_hits=$hits;
	    metadata_file=`echo $file | perl -pe 's/\.txt/\.metadata/;'`;
	    if ! [ "$hits" = "1" -o "$hits" = "0" ]; then
		# filter out lines that contain the date (original files sometimes have the same name, e.g. "gradu.pdf")
		date=`echo $file | perl -pe 's/.*_DATE=([0-9]{4}(\-[0-9]{2})?(\-[0-9]{2})?).*/\(citation_\)\?date="\1/'`;
		dateregexp=`echo $date | perl -pe 's/\-/\\\\-/g;'`;
		# echo "REGEXP: "$dateregexp;
		cat hits | egrep $dateregexp > tmp;
		mv tmp hits;
		cp hits $file.hits2;
		hits=`wc -l hits | perl -pe 's/^([0-9]+).*/\1/;'`;
		if [ "$hits" = "1" ]; then
		    cat hits | perl -C -pe 's/  +/ /; s/\x{2028}//;' > $metadata_file;
		fi
	    else
		if [ "$hits" = "1" ]; then
		    cat hits | perl -C -pe 's/  +/ /;  s/\x{2028}//;' > $metadata_file;
		fi
	    fi
	    # echo "ethesis_en/"$dir"/"$subdir"/"$file": "$hits" ("$orig_hits")";
	    # echo $file | perl -pe 's/\n/\t/;' >> GREP;
	    # echo $hits >> GREP;
	done
	cd ..;
    done
    cd ..;
done
cd ..;

# 40 cases that must be handled manually:
# egrep -v ': 1 ' | grep '('
