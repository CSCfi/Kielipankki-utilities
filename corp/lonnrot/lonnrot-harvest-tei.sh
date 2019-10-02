#! /bin/sh

# Harvest all TEI source files as a single zip file from
# http://lonnrot.finlit.fi/omeka
#
# Usage: lonnrot-harvest-tei.sh [tei_file]
#
# The output file is
# /v/corpora/src/lonnrot/Lonnrot_TEI_orig_YYYYMMDD.zip, unless
# otherwise specified via the command-line argument.
#
# The script harvests the TEI files by collection to work around a
# problem in downloading the TEI data for all the collections as a
# single file.
#
# Jyrki Niemi
# FIN-CLARIN <https://www.kielipankki.fi/organization/fin-clarin/>
# University of Helsinki <https://www.helsinki.fi/en/>
# 2019-10-02


tmpdir=${TMPDIR:-/tmp}/$(basename $0).$$

tei_file=/v/corpora/src/lonnrot/Lonnrot_TEI_orig_$(date +%Y%m%d).zip
if [ "x$1" != x ]; then
    tei_file=$1
fi
mkdir -p "$tmpdir"

lonnrot_url_base="http://lonnrot.finlit.fi/omeka/"
coll_list_url_base="$lonnrot_url_base/collections?sort_field=added&page="
coll_url_base="$lonnrot_url_base/items/browse?tei=&collection="

page=1
while true; do
    out_fname=$(printf "$tmpdir/coll_list_%03d.html" $page)
    wget --random-wait -O "$out_fname" "$coll_list_url_base$page"
    if ! grep -E -q '/omeka/items/browse\?collection=' "$out_fname"; then
	rm "$out_fname"
	break
    fi
    page=$(($page + 1))
done

grep -E -o '/omeka/items/browse\?collection=[0-9]+' "$tmpdir"/coll_list_*.html |
    sed -e 's/.*=//' |
    sort -u |
    while read coll; do
	out_fname=$(printf "$tmpdir/coll_%03d.zip" $coll)
	wget --random-wait -O "$out_fname" --post-data 'tei=Submit+Query' \
	     "$coll_url_base$coll"
	# Extract to $tmpdir (-d)
	unzip -d "$tmpdir" "$out_fname"
    done

(
    cd "$tmpdir"
    zip "$tei_file" *.xml
)

# rm -rf "$tmpdir"
