#!/bin/sh

# 1) generate filenames for files whose language has not been marked:
# i.e. prepend the output of lang_recognizer.py to the filename

for dir in gradut vaitokset;
do
  cd $dir;
  for subdir in aleksanteri-instituutti bio_ja_ymparistot elainlaaketiede farmasia humanistinen kayttaytymistiede laaketiede maajametsatiede matemaattis oikeustiede teologinen valtiotiede;
  do
      if (ls $subdir > /dev/null 2> /dev/null); then
	  if [ "$1" = "--verbose" -o "$2" = "--verbose" ]; then echo "Guessing language and renaming files for "$dir"/"$subdir; fi
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

if (ls ethesis_en > /dev/null 2> /dev/null); then
    echo "Directory ethesis_en exists";
    exit 1;
fi

if [ "$1" = "--verbose" -o "$2" = "--verbose" ]; then echo "Copying English files"; fi

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

