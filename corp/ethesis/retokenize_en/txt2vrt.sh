#!/bin/sh

# - newer gradut package contains dir matemaattis with 577 files
# - newer gradut package contains 1203 more files
# - older gradut package contains one file that is not in newer package: teologinen/tuhoa.zip
# - both packages contain "Hot Folder Log.txt", category.txt and logfile.txt files
# - gradutiivistelmat is not in IDA in txt format? 2016 files in package

# "You do not have the credentials to access the restricted item hdl:10138/165906. The selected item is withdrawn and is no longer available."

if !(ls lang_recognizer.py > /dev/null 2> /dev/null); then
    echo "lang_recognizer.py not found in the current directory";
    exit 1;
fi

for packagedir in E-thesis_gradut_TXT_2016-11-22 E-thesis_other_langs_VRT_2016-11-22;
do
    if !(ls $packagedir > /dev/null 2> /dev/null); then
	echo "Package directory "$packagedir" not found in the current directory";
	exit 1;
    fi
done

# copy files from IDA packages

if [ "$1" = "--verbose" ]; then echo "Copying files from IDA packages"; fi

if !(ls gradut/ > /dev/null 2> /dev/null); then
    mkdir gradut ;
    cd gradut ;
    cp -R ../E-thesis_gradut_TXT_2016-11-22/* . ;
    cp ../E-thesis_other_langs_VRT_2016-11-22/ethesis_en_ma_mm.vrt maajametsatiede/metadata_vrt ;
    cp ../E-thesis_other_langs_VRT_2016-11-22/ethesis_en_ma_sci.vrt matemaattis/metadata_vrt ;
    cp ../E-thesis_other_langs_VRT_2016-11-22/ethesis_en_ma_valt.vrt valtiotiede/metadata_vrt ;
    cd .. ;
fi

if !(ls vaitokset/ > /dev/null 2> /dev/null); then
    mkdir vaitokset ;
    cd vaitokset ;
    cp -R ../E-thesis_vaitokset_TXT_2016-10-17/* . ;
    # harmonize directory names
    mv beh kayttaytymistiede ;
    mv bio bio_ja_ymparistot ;
    mv elain elainlaaketiede ;
    mv maajametsa maajametsatiede ;
    mv matematiikka matemaattis ;
    mv med laaketiede ;
    mv oikeus oikeustiede ;
    cd .. ;
fi

# harmonize metadata filenames
for file in gradut/*/logfile.txt;
do
    echo $file | perl -pe 's/^(.*)\/logfile\.txt$/mv \1\/logfile.txt \1\/metadata_txt/;' | sh;
done
for file in gradut/*/read.me;
do
    echo $file | perl -pe 's/^(.*)\/read\.me$/mv \1\/read.me \1\/metadata_txt/;' | sh;
done
for file in vaitokset/*/logfile.txt;
do
    echo $file | perl -pe 's/^(.*)\/logfile\.txt$/mv \1\/logfile.txt \1\/metadata_txt/;' | sh;
done

for file in gradut/*/metadata_txt gradut/*/metadata_vrt vaitokset/*/metadata_txt ;
do
    cat $file | perl -pe "s/(\|\|\|<text )/\n\1/g;" > tmp;
    mv tmp $file;
done

# 1) generate filenames for files whose language has not been marked:
# i.e. prepend the output of lang_recognizer.py to the filename

for dir in gradut vaitokset;
do
  cd $dir;
  for subdir in aleksanteri-instituutti bio_ja_ymparistot elainlaaketiede farmasia humanistinen kayttaytymistiede laaketiede maajametsatiede matemaattis oikeustiede teologinen valtiotiede;
  do
      if (ls $subdir > /dev/null 2> /dev/null); then
	  if [ "$1" = "--verbose" ]; then echo "Guessing language and renaming files for "$dir"/"$subdir; fi
	  cd $subdir;
	  # e.g. _t_2016utkielma.txt -> fi_t_2016utkielma.txt
	  for file in `ls *.txt | grep -v 'Hot Folder Log' | grep -v 'logfile\.txt' | grep -v 'read\.me' | grep -v 'category\.txt' | egrep -v '\(2\)' | egrep -v '(en_|eng_|fi_|fin_|sv_|swe_|ru_|de_|es_|fr_|it_|pol_|other_)'`;
	  do
	      lang=`cat $file | python3 -c 'import sys; sys.path.insert(0, "../.."); from lang_recognizer import recognize; import sys; print(recognize(sys.stdin.read()));' | perl -pe 's/\n//;'`;
	      newfile=`echo $file | perl -pe 's/^([^_])/_\1/; s/^/'$lang'/;'`;
	      mv $file $newfile;
	  done;
	  for file in `ls *.txt | grep -v 'Hot Folder Log' | grep -v 'logfile\.txt' | grep -v 'read\.me' | grep -v 'category\.txt' | egrep -v '\(2\)'`;
	  do
	      # e.g. fi_t_2016utkielma.txt -> fi_tutkielma_DATE=2016.txt, en_m_2013-05-29aster_thesis.txt -> en_master_thesis_DATE=2013-05-29.txt
	      # (checked that there will not be identical filenames in the same directory)
	      newfile=`echo $file | perl -pe 'if (m/^[^_]+_([^_])_[0-9]{4}(\-[0-9]{2})?(\-[0-9]{2})?/) { s/^([^_]+_)([^_])_([0-9]{4}(\-[0-9]{2})?(\-[0-9]{2})?)(.*)\.txt/\1\2\6_DATE=\3.txt/; } else { $_=""; }'`;
	      if [ "$subdir" = "oikeustiede" -o "$subdir" = "valtiotiede" ]; then
		  # some files have T, 6 digits and Z added in between
		  newfile=`echo $newfile | perl -pe 's/T[0-9]{6}Z//;'`;
	      fi
	      if ! [ "$newfile" = "" ]; then
		  mv $file $newfile;
	      fi
	  done
	  # copy English files to a separate directory
	  if !(ls en/ > /dev/null 2> /dev/null); then
	      mkdir en;
	  fi
	  for file in `ls *.txt | egrep -v '\(2\)' | egrep '^(en_|eng_)'`;
	  do
	      no_prefix=`echo $file | perl -pe 's/^(en_|eng_)//;'`;
	      cp $file en/$no_prefix;
	  done
	  cd ..;
      fi;
  done;
  cd ..;
done

if [ "$1" = "--verbose" ]; then echo "Copying English files"; fi

mkdir ethesis_en;
mkdir ethesis_en/gradut;
mkdir ethesis_en/vaitokset;
for subdir in bio_ja_ymparistot elainlaaketiede farmasia humanistinen kayttaytymistiede laaketiede maajametsatiede matemaattis oikeustiede teologinen valtiotiede;
do
    mkdir ethesis_en/gradut/$subdir;
    mkdir ethesis_en/vaitokset/$subdir;
    cp gradut/$subdir/en/*.txt ethesis_en/gradut/$subdir/;
    if ! [ "$subdir" = "maajametsatiede" -o "$subdir" = "matemaattis" -o "$subdir" = "valtiotiede" ]; then
	cp gradut/$subdir/metadata_txt ethesis_en/gradut/$subdir/;
    else
	cp gradut/$subdir/metadata_vrt ethesis_en/gradut/$subdir/;
    fi
    cp vaitokset/$subdir/en/*.txt ethesis_en/vaitokset/$subdir/;
    cp vaitokset/$subdir/metadata_txt ethesis_en/vaitokset/$subdir/;
done
mkdir ethesis_en/gradut/aleksanteri-instituutti;
cp gradut/aleksanteri-instituutti/en/*.txt ethesis_en/gradut/aleksanteri-instituutti/;
cp gradut/aleksanteri-instituutti/metadata_txt ethesis_en/gradut/aleksanteri-instituutti/;

# get metadata from logfile.txt or read.me, e.g.
# for file in *; do echo $file | perl -pe 's/\n/\t/;' && (echo $file | perl -pe 's/_[0-9]{4}\.txt/\\.pdf/; s/^(.*)$/grep -c "\1" ..\/..\/..\/E-thesis_gradut_TXT_2016-11-22\/humanistinen\/read.me/;') | sh ; done

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
	if [ "$1" = "--verbose" ]; then echo "Grepping metadata for "$dir"/"$subdir; fi
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
		    cp hits $metadata_file;
		fi
	    else
		if [ "$hits" = "1" ]; then
		    cp hits $metadata_file;
		fi
	    fi
	    echo "ethesis_en/"$dir"/"$subdir"/"$file": "$hits" ("$orig_hits")";
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

# Combine hundred files in a directory into a single directory for faster parsing
# At this point, remove also some strange characters
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
	nall="0"; # ALL1, ALL2, ...
	nfiles="0";
	for file in *.txt;
	do
	    nfiles=$((nfiles + 1));
	    if [ "$((nfiles % 100))" = "1" ]; then
		nall=$((nall + 1));
		touch "ALL"$nall.TXT;
		echo "Creating file "$dir"/"$subdir"/ALL"$nall.TXT"...";
	    fi
	    # the parser drops some comment lines out, try multiple lines?
	    echo "" >> "ALL"$nall.TXT;
	    for n in 1 2 3 4 5;
	    do
		echo "###C: FILENAME: "$file >> "ALL"$nall.TXT;
	    done
	    echo "" >> "ALL"$nall.TXT;
	    # - remove control characters U+0000 - U+001F (excluding TAB U+0009, LF U+000A and CR U+000D) and U+007F - U+009F,
	    #   Unicode line and paragraph separators (U+2028, U+2029) and soft hyphens (U+00AD) and some other strange characters
	    # - convert FIGURE SPACE (U+2007) and NARROW NO-BREAK SPACE (U+202F) (and also THIN SPACE, U+2009) to NBSPs
	    # - convert other spaces into oridinary spaces
	    cat $file | perl -C -pe 's/[\x{0000}-\x{0008}\x{000B}\x{000C}\x{000E}-\x{001F}\x{00AD}\x{007F}-\x{009F}\x{2028}\x{2029}\x{00AD}\x{2028}\x{FEFF}\x{FFFF}]//g; s/[\x{2007}\x{202F}\x{2009}]/\x{00A0}/g; s/[\x{0085}\x{1680}\x{2000}-\x{200A}\x{202F}\x{205F}\x{3000}]/ /g;' >> "ALL"$nall.TXT;
	    echo "" >> "ALL"$nall.TXT;
	done
	cd ..;
    done
    cd ..;
done
cd ..;

# parse all files
for file in ethesis_en/*/*/ALL*.TXT; do echo "Parsing "$file && cat $file | perl -pe 's/^/\n/;' | python3 full_pipeline_stream.py --gpu -1 --conf models_en_ewt/pipelines.yaml parse_plaintext > `echo $file | perl -pe 's/ALL([0-9]+)\.TXT/ALL\1.CONLLU/;'`; done

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
	    cat $file | ./split-conllu-files.pl;
	done
	rm split-conllu-files.pl;
	for conllufile in *.conllu;
	do
	    prevrtfile=`echo $conllufile | perl -pe 's/\.conllu/\.prevrt/;'`;
	    metadatafile=`echo $conllufile | perl -pe 's/\.conllu/\.metadata/;'`;
	    vrtfile=`echo $conllufile | perl -pe 's/\.conllu/\.vrt/;'`;
	    cat $conllufile | perl -pe 's/^# newpar/<paragraph>/; s/^# sent_id = ([0-9]+)/<sentence id="\1">/; s/^# text .*//; s/^# newdoc//;' | ../../../add-missing-tags.pl | perl -pe 's/^\n$//g;' > $prevrtfile;
	    (echo '<!-- #vrt positional-attributes: id word lemma upos xpos feats head deprel deps misc -->'; cat $metadatafile | perl -pe 's/\&/&amp;/g;' | perl -pe "s/'/&apos;/g;"; cat $prevrtfile; echo "</text>") > $vrtfile;
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

# get metadata file
#for file in ethesis_en/*/*/*.conllu;
#do
#    metadatafile=`echo $file | perl -pe 's/\.conllu/\.metadata/;'`;
#    hitsfile2=`echo $file | perl -pe 's/\.conllu/\.hits2/;'`;
#    hitsfile1=`echo $file | perl -pe 's/\.conllu/\.hits/;'`;
#
#    if (ls $hitsfile1 > /dev/null 2> /dev/null); then
#	hits=`wc -l $hitsfile1`;
#	if [ "$hits" = "1" ]; then
#	    cp $hitsfile1 $metadatafile;
#	fi
#    fi
#    if (ls $hitsfile2 > /dev/null 2> /dev/null); then
#	hits=`wc -l $hitsfile2`;
#	if [ "$hits" = "1" ]; then
#	    cp $hitsfile2 $metadatafile;
#	fi
#    fi
#done

# cat file.txt | perl -pe 's/^/\n/;' | python3 full_pipeline_stream.py --gpu -1 --conf models_en_ewt/pipelines.yaml parse_plaintext > file.conllu;
# cat file.conllu | perl -pe 's/^# newpar/<paragraph>/; s/^# sent_id = ([0-9]+)/<sentence id="\1">/; s/^# text .*//; s/^# newdoc//;' | ./add-missing-tags.pl > file.prevrt
# (echo '<!-- #vrt positional-attributes: id word lemma upos xpos feats head deprel deps misc -->'; cat file.metadata file.prevrt; echo "</text>") > file.vrt; 
#
# $vrttools/vrt-keep -i -n 'word,id,lemma,upos,xpos,feats,head,deprel,deps,misc' file.vrt;
# $vrttools/vrt-rename -i -m id=ref -m head=dephead -m feats=msd -m upos=pos file.vrt;
# cat file | ./msd-bar-to-space.pl > tmp && mv tmp file.vrt;


# neither
# gradut: maajametsatiede matemaattis valtiotiede

# or from VRT file, e.g.

# 3) generate original pdf filename from filename in TXT package:
# PDF-TO-TXT conversion seems to work like this: original.pdf -> {LANG}_o_{YEAR}_riginal.txt
# echo FILENAME.txt | perl -pe 's/^[^_]+_([^_])_[0-9]{4}(.*)\.txt/\1\2\.pdf/;' > FILENAME.pdf
# original pdf filename can be used as a search criterion to extract
# (missing) metadata from the VRT file:
# grep 'pdfurl="FILENAME\.pdf"' ethesis_en_ma_{FACULTY}.vrt

# possibly rename all txt filenames to conform with the pdf filename

# 4) generate VRT file from metadata and txt file

# 5) run the VRT files through TNPP (ewt model seems to perform best)

# 6) then korp-make etc.

# Faculty abbreviations and other information about the packages:
# 
# E-thesis_gradut_	E-thesis_vaitokset_	korp		vrt	logfile.txt
# TXT_2016-11-22.zip	TXT_2016-10-17.zip	configuration	package	or read.me
# ------------------	-------------------	-------------	-------	-----------
# 
# aleksanteri-instituutti	--			ai					
# bio_ja_ymparistot	bio			bio
# elainlaaketiede		elain			elain		not MA
# farmasia		farmasia		far
# humanistinen		humanistinen		hum		not MA
# kayttaytymistiede	beh			beh
# laaketiede		med			med		not MA
# maajametsatiede		maajametsa		mm			not MA
# matemaattis		matematiikka		sci, math		not MA
# oikeustiede		oikeus			ot
# teologinen		teologinen		teo
# valtiotiede		valtiotiede		valt			not MA
