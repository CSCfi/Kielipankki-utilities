#!/bin/sh

verbose="false";
vrttooldir=""
for arg in $@;
do
    if [ "$vrttooldir" = "<next>" ]; then
	vrttooldir=$arg"/";
    fi
    if [ "$arg" = "--vrt-tool-dir" ]; then
	vrttooldir="<next>";
    fi
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
	    echo "Generating VRT files in directory "$dir"/"$subdir;
	fi
	for conllufile in *.conllu;
	do
	    prevrtfile=`echo $conllufile | perl -pe 's/\.conllu/\.prevrt/;'`;
	    metadatafile=`echo $conllufile | perl -pe 's/\.conllu/\.metadata/;'`;
	    vrtfile=`echo $conllufile | perl -pe 's/\.conllu/\.vrt/;'`;
	    cat $conllufile | perl -pe 's/^# newpar/<paragraph>/; s/^# sent_id = ([0-9]+)/<sentence id="\1">/; s/^# text .*//; s/^# newdoc//; s/^# *//;' | ../../../add-missing-tags.pl | perl -pe 's/^\n$//g;' > $prevrtfile;
	    (echo '<!-- #vrt positional-attributes: id word lemma upos xpos feats head deprel deps misc -->'; (cat $metadatafile 2> /dev/null || echo "<text>") | \
														  perl -pe 's/\&/&amp;/g;' | perl -pe "s/'/&apos;/g;"; cat $prevrtfile; echo "</text>") > $vrtfile;
	    #cat $vrtfile | ./renumber-sentences.pl > tmp && mv tmp $vrtfile;
	    # cp $vrtfile $vrtfile.bak;
	    $vrttooldir/vrt-keep -i -n 'word,id,lemma,upos,xpos,feats,head,deprel,deps,misc' $vrtfile;
	    $vrttooldir/vrt-rename -i -m id=ref -m head=dephead -m feats=msd -m upos=pos $vrtfile;
	    # cat file | ./msd-bar-to-space.pl > tmp && mv tmp $vrtfile;

	done
	cd ..;
    done
    cd ..;
done
cd ..;
