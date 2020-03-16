#!/bin/sh

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    echo ""
    echo "Usage: ha-process.sh SFMFILE CORPUSNAME [--sentences|--stories] [--datefrom DATE] [--dateto DATE] [--corpusdir DIR]"
    echo ""
    exit 0
fi

cwb_bindir=/usr/local/cwb-3.4.12/bin/
corpus_root=`pwd`
PYTHON=python
from_encoding="ISO-8859-1"
to_encoding="utf-8"
KIELIPANKKI_TOOLDIR=~/Kielipankki-konversio/scripts

datefrom=""
dateto=""
corpusdir=""
SFM_TO_VRT_TOOL=""

for arg in "$@"
do
    if [ "$datefrom" = "next..." ]; then
	datefrom=$arg
    elif [ "$dateto" = "next..." ]; then
	dateto=$arg
    elif [ "$corpusdir" = "next..." ]; then
	corpusdir=$arg
    elif [ "$arg" = "--datefrom" ]; then
	datefrom="next..."
    elif [ "$arg" = "--dateto" ]; then
	dateto="next..."
    elif [ "$arg" = "--corpusdir" ]; then
	corpusdir="next..."
    elif [ "$arg" = "--stories" ]; then
	SFM_TO_VRT_TOOL="sfm2vrt-stories.py"
    elif [ "$arg" = "--sentences" ]; then
	SFM_TO_VRT_TOOL="sfm2vrt-sentences.py"
    fi
done

if [ "$SFM_TO_VRT_TOOL" = "" ]; then
    echo "Missing option: --stories or --sentences"
    exit 1
fi

cp $1 tmp
dos2unix tmp
sed -i '/^\s*$/d' tmp
iconv -f $from_encoding -t $to_encoding < tmp > TMP
mv TMP tmp

if ! ($PYTHON ./$SFM_TO_VRT_TOOL tmp TMP); then
    echo "Error: in "$SFM_TO_VRT_TOOL", exiting..."
    exit 1
fi
./postprocess-ha-whitespace-and-punctuation.pl < TMP > tmp1
./postprocess-ha-add-lemmas.pl < tmp1 > TMP
./postprocess-ha-empty-fields-and-special-characters.pl < TMP > tmp1

echo '<text filename="'$2'" datefrom="'$datefrom'" dateto="'$dateto'" timefrom="000000" timeto="235959">' > tmp
cat tmp1 >> tmp
echo "</text>" >> tmp
mv tmp $2.vrt

export CWB_BINDIR=$cwb_bindir
if ! [ -d "registry" ]; then
    mkdir registry
fi

$KIELIPANKKI_TOOLDIR/korp-make --corpus-root=$corpus_root --log-file=log --no-lemgrams --no-lemmas-without-boundaries --no-logging --verbose --input-attributes "lemma morph gloss pos" $2 $2.vrt

c=$(echo $corpusdir | perl -pe 's/\//\\\//g;')

if ! [ "corpusdir" = "" ]; then
    perl -i -pe 's/^HOME .*/HOME '$c'\/data\/'$2'/;' registry/$2
    perl -i -pe 's/^INFO .*/INFO '$c'\/data\/'$2'\/\.info/;' registry/$2
fi

# sudo cp -R data/$2/* /usr/lib/cgi-bin/corpora/data/$2/
# sudo cp -R registry/$2 /usr/lib/cgi-bin/corpora/registry/$2
