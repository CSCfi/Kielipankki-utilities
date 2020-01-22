#!/bin/sh

vrttools=$1;

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
	for conllufile in *.conllu;
	do
	    prevrtfile=`echo $conllufile | perl -pe 's/\.conllu/\.prevrt/;'`;
	    metadatafile=`echo $conllufile | perl -pe 's/\.conllu/\.metadata/;'`;
	    vrtfile=`echo $conllufile | perl -pe 's/\.conllu/\.vrt/;'`;
	    cat $conllufile | perl -pe 's/^# newpar/<paragraph>/; s/^# sent_id = ([0-9]+)/<sentence id="\1">/; s/^# text .*//; s/^# newdoc//; s/^# *//;' | ../../../add-missing-tags.pl | perl -pe 's/^\n$//g;' > $prevrtfile;
	    (echo '<!-- #vrt positional-attributes: id word lemma upos xpos feats head deprel deps misc -->'; (cat $metadatafile || echo "<text>") | \
														  perl -pe 's/\&/&amp;/g;' | perl -pe "s/'/&apos;/g;"; cat $prevrtfile; echo "</text>") > $vrtfile;
	    #cat $vrtfile | ./renumber-sentences.pl > tmp && mv tmp $vrtfile;
	    # cp $vrtfile $vrtfile.bak;
	    $vrttools/vrt-keep -i -n 'word,id,lemma,upos,xpos,feats,head,deprel,deps,misc' $vrtfile;
	    $vrttools/vrt-rename -i -m id=ref -m head=dephead -m feats=msd -m upos=pos $vrtfile;
	    # cat file | ./msd-bar-to-space.pl > tmp && mv tmp $vrtfile;

	done
	cd ..;
    done
    cd ..;
done
cd ..;
