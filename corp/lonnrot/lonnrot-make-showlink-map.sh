#! /bin/sh

# Generate links to lonnrot.finlit.fi based on Dublin Core metadata
# files and a zip file containing the TEI XML files.
#
# Usage: lonnrot-make-showlink-map.sh lonnrot_TEI.zip [dcmes_dir]
#        > lonnrot-xml-showlink-map.tsv
#
# Jyrki Niemi
# FIN-CLARIN <https://www.kielipankki.fi/organization/fin-clarin/>
# University of Helsinki <https://www.helsinki.fi/en/>
# 2019-02-20


tei_zip=$1
dcmes_dir=/v/corpora/src/lonnrot/dcmes-xml-$(date +%Y%m%d)
if [ "x$2" != x ]; then
    dcmes_dir=$2
fi
prefix=$dcmes_dir/lonnrot-dcmes

LC_ALL=C
export LC_ALL

texts_file=${TMPDIR:/tmp}/lonnrot_texts_$$.tsv

unzip -v "$tei_zip" |
    grep -E '[0-9]+_.*\.xml' |
    awk '{print $NF}' |
    perl -ne '/^(\d+)_/; print "$1\t$_";' |
    sort -k1,1 > $texts_file

grep -E 'rdf:about|dc:identifier' "$prefix"-*.xml |
    perl -ne 'if (/rdf:about="(.*?)"/) {
                  $url = $1
              } elsif (/<dc:identifier>(\d+)</) {
                  print "$1\t$url\n"
	      }' |
    LC_ALL=C sort -k1,1 |
    LC_ALL=C join -t'	' -j1 -a1 -o "1.2 2.2" $texts_file - |
    sort -n

# rm $texts_file
