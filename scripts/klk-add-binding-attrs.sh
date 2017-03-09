#! /bin/sh
# -*- coding: utf-8 -*-


# Add the s-attributes text_binding_id and text_publ_type to the KLK
# corpora specified as command-line arguments


progdir=$(dirname $0)

origdatadir=/v/corpora/vrt/klk_links
cwb_regdir=/v/corpora/registry
cwb_datadir=/v/corpora/data
cwb_bindir=/usr/local/cwb/bin

origdatafile=$origdatadir/digi_content.csv
binding_info_file=$origdatadir/binding_info.tsv

export LC_ALL=C


init () {
    if ! [ -s $binding_info_file ]; then
	$progdir/klk-extract-binding-info.py $origdatafile |
	LC_ALL=C sort > $binding_info_file
    fi
}

add_attr () {
    corpus=$1
    elem=$2
    attrname=$3
    regfile=$cwb_regdir/$corpus
    # Edit registry file directly instead of using cwb-regedit so that
    # the attribute is added to the same group "XML element"
    grep -q "^STRUCTURE ${elem}_$attrname " $regfile || {
	cp -p $regfile $regfile.old
	awk '/^# <'$elem' / { sub (/">/, "\" '$attrname'=\"..\">") }
             /^STRUCTURE '$elem'[ _]/ { elems = 1 }
             /^$/ && elems {
                 printf "STRUCTURE %-20s # [annotations]\n", "'${elem}_$attrname'";
                 elems = 0 }
             { print }' \
		 $regfile.old > $regfile
    }
    # cwb-regedit -r $cwb_regdir $(echo $corpus | sed -e 's/.*/\U&\E/') \
    # 	:add :s text_$attrname    
}

encode () {
    corpus=$1
    attrname=$2
    fields=$3
    cut -d'	' -f$fields $origdatadir/binding_info_$corpus.tsv |
    $cwb_bindir/cwb-s-encode -r $cwb_regdir -d $cwb_datadir/$corpus \
	-V text_$attrname
    add_attr $corpus text $attrname
}    

add_binding () {
    corpus=$(basename $1)
    $cwb_bindir/cwb-s-decode -r $cwb_regdir $corpus -S text_img_url |
    perl -ne '/(.*\t)#DIRECTORY#(.*?)#SEPARATOR#/; print "$1$2\n"' |
    sort -t'	' -s -k3,3 > $origdatadir/img_urls_$corpus.tsv
    join -t'	' -13 -21 -a1 -o '1.1 1.2 1.3 2.2 2.3' \
	$origdatadir/img_urls_$corpus.tsv $binding_info_file |
    sort -s -k1,1n > $origdatadir/binding_info_$corpus.tsv
    encode $corpus binding_id 1,2,4
    encode $corpus publ_type 1,2,5
}


init

for corpus in $@; do
    echo $corpus
    add_binding $corpus
done
