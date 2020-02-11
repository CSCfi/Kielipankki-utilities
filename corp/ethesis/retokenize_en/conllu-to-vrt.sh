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

# text attributes "type" and "faculty_directory"
text_type=""; # add if missing
text_faculty_directory=""; # add to all texts

cd ethesis_en;
for dir in gradut vaitokset;
do
    if [ "$dir" = "gradut" ]; then
	text_type="Master&apos;s thesis";
    else
	text_type="Doctoral dissertation";
    fi

    cd $dir;
    subdirs="bio_ja_ymparistot elainlaaketiede farmasia humanistinen kayttaytymistiede laaketiede maajametsatiede matemaattis oikeustiede teologinen valtiotiede";
    if [ "$dir" = "gradut" ]; then
	subdirs="aleksanteri-instituutti "$subdirs;
    fi
    for subdir in $subdirs;
    do
	case "$subdir" in
	    "aleksanteri-instituutti") text_faculty_directory="Aleksanteri Institute"
	    ;;
	    "bio_ja_ymparistot") text_faculty_directory="Faculty of Biological and Environmental Sciences"
	    ;;
	    "elainlaaketiede") text_faculty_directory="Faculty of Veterinary Medicine"
	    ;;
	    "farmasia") text_faculty_directory="Faculty of Pharmacy"
	    ;;
	    "humanistinen") text_faculty_directory="Faculty of Arts"
	    ;;
	    "kayttaytymistiede") text_faculty_directory="Faculty of Behavioural Sciences"
	    ;;
	    "laaketiede") text_faculty_directory="Faculty of Medicine"
	    ;;
	    "maajametsatiede") text_faculty_directory="Faculty of Agriculture and Forestry"
	    ;;
	    "matemaattis") text_faculty_directory="Faculty of Science"
	    ;;
	    "oikeustiede") text_faculty_directory="Faculty of Law"
	    ;;
	    "teologinen") text_faculty_directory="Faculty of Theology"
	    ;;
	    "valtiotiede") text_faculty_directory="Faculty of Social Sciences"
	    ;;
	esac

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
														  perl -pe 's/\&/&amp;/g;' | perl -pe "s/'/&apos;/g;" | perl -pe 's/ +/ /g; s/ "/"/g;'; cat $prevrtfile; echo "</text>") > $vrtfile;
	    #cat $vrtfile | ./renumber-sentences.pl > tmp && mv tmp $vrtfile;
	    # cp $vrtfile $vrtfile.bak;
	    $vrttooldir/vrt-keep -i -n 'word,id,lemma,upos,xpos,feats,head,deprel,deps,misc' $vrtfile;
	    $vrttooldir/vrt-rename -i -m id=ref -m head=dephead -m feats=msd -m upos=pos $vrtfile;
	    # cat file | ./msd-bar-to-space.pl > tmp && mv tmp $vrtfile;
	    #
	    # harmonize attribute names, add missing attributes with an empty value, represent empty values as "_":
	    #
	    perl -pe 'if (/^<text[ >]/) { s/ citation_(title|date|keywords=")/ \1/g; s/citation_abstract_html_url="/url="/; s/=""/="_"/g; }';
	    perl -pe 'if (/^<text[ >]/) { foreach my $attr ("citation_language","citation_authors","url","keywords","citation_pdf_url","date","title","faculty","subject","type","datefrom","dateto") { unless (/${attr}="/) { s/>/ ${attr}="_">/; } } }';
	    # - add datefrom and dateto (these are missing from 40 files that don't have a metadata file)
	    # - add timefrom="000000" timeto="235959" (no file has these, but korp requires them?)
	    #
	    # Add type, if empty. Define faculty directory.
	    # (text_faculty_directory and text_type contain spaces so they must be surrounded by double quotes)
	    # the perl statement consists of:
	    # -  'if (/^<text /) { s/>/ faculty_directory="'
	    # -  "$text_faculty_directory"
	    # -  '">/; s/type="_"/type="'
	    # -  "$text_type"
	    # -  '"/; }'
	    perl -pe 'if (/^<text /) { s/>/ faculty_directory="'"$text_faculty_directory"'">/; s/type="_"/type="'"$text_type"'"/; }'

	done
	cd ..;
    done
    cd ..;
done
cd ..;
