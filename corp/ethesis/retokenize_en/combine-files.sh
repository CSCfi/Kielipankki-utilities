#!/bin/sh

# Combine 50 files in a directory into a single directory for faster parsing
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
	    if [ "$((nfiles % 50))" = "1" ]; then
		nall=$((nall + 1));
		rm --force "ALL"$nall.TXT;
		touch "ALL"$nall.TXT;
		if [ "$1" = "--verbose" -o "$2" = "--verbose" ]; then
		    echo "Creating file "$dir"/"$subdir"/ALL"$nall.TXT"...";
		fi
	    fi
	    echo "" >> "ALL"$nall.TXT;
	    echo "###C: " >> "ALL"$nall.TXT;
	    echo '"FILENAME_'$file'"' >> "ALL"$nall.TXT;
	    echo "###C: " >> "ALL"$nall.TXT;
	    echo "" >> "ALL"$nall.TXT;
	    # - remove control characters U+0000 - U+001F (excluding TAB U+0009, LF U+000A and CR U+000D) and U+007F - U+009F,
	    #   Unicode line and paragraph separators (U+2028, U+2029) and soft hyphens (U+00AD) and some other strange characters
	    # - convert FIGURE SPACE (U+2007) and NARROW NO-BREAK SPACE (U+202F) (and also THIN SPACE, U+2009) to NBSPs
	    # - convert other spaces into oridinary spaces
	    if [ "$1" = "--test" -o "$2" = "--test" ]; then
		head -10 $file > tmp;
	    else
		cat $file > tmp;
	    fi
	    cat tmp | perl -C -pe 's/[\x{0000}-\x{0008}\x{000B}\x{000C}\x{000E}-\x{001F}\x{00AD}\x{007F}-\x{009F}\x{2028}\x{2029}\x{00AD}\x{2028}\x{FEFF}\x{FFFF}]//g; s/[\x{2007}\x{202F}\x{2009}]/\x{00A0}/g; s/[\x{0085}\x{1680}\x{2000}-\x{200A}\x{202F}\x{205F}\x{3000}]/ /g;' >> "ALL"$nall.TXT;
	    rm tmp;
	    echo "" >> "ALL"$nall.TXT;
	done
	cd ..;
    done
    cd ..;
done
cd ..;
