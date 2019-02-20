#! /bin/sh

# Harvest Dublin Core XML metadata from
# http://lonnrot.finlit.fi/omeka, for generating links to
# lonnrot.finlit.fi.
#
# Usage: lonnrot-harvest-dcmes.sh [dcmes_dir]
#
# By default, the script outputs the metadata files to directory
# /v/corpora/src/lonnrot/dcmes-xml-YYYYMMDD.
#
# Jyrki Niemi
# FIN-CLARIN <https://www.kielipankki.fi/organization/fin-clarin/>
# University of Helsinki <https://www.helsinki.fi/en/>
# 2019-02-20


dcmes_dir=/v/corpora/src/lonnrot/dcmes-xml-$(date +%Y%m%d)
if [ "x$1" != x ]; then
    dcmes_dir=$1
fi
mkdir -p "$dcmes_dir"
prefix=$dcmes_dir/lonnrot-dcmes
lonnrot_url_base="http://lonnrot.finlit.fi/omeka/items?&output=dcmes-xml&page="

page=1
while true; do
    out_fname=$(printf "$prefix-%03d.xml" $page)
    wget --random-wait -O "$out_fname" "$lonnrot_url_base$page"
    if ! grep -q rdf:Description "$out_fname"; then
	break
	rm "$out_fname"
    fi
    page=$(($page + 1))
done
