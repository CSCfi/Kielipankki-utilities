#! /bin/bash
# -*- coding: utf-8 -*-

# Make a parsed version of the Finnish National Library corpus


progname=$0

corproot=/v/corpora
regdir=$corproot/registry
vrtdir=$corproot/vrt
orig_vrt_dir=$vrtdir/klk_fi
parsed_vrt_dir=$vrtdir/klk_fi_parsed
dbdir=$corproot/conll09
cwbdir=/usr/local/cwb/bin

cwb_encode=$cwbdir/cwb-encode
cwb_make=/usr/local/bin/cwb-make
scriptdir=/home/janiemi/finclarin/korp-git/corp/scripts
lemgram_posmap=$parsed_vrt_dir/lemgram_posmap_tdt.txt

struct_attrs='-S text:0+issue_date+sentcount+language+elec_date+dateto+datefrom+img_url+label+publ_part+issue_no+tokencount+part_name+publ_title+publ_id+page_id+page_no+issue_title -S paragraph:0+id -S sentence:0+local_id+parse_state+id'
pos_attrs='-P lemma -P lemmacomp -P pos -P msd -P dephead -P deprel -P ref -P ocr -P lex'

verbose=1

export TIMEFORMAT="    %U + %S s"

echo_verb () {
    if [ "x$verbose" != "x" ]; then
	echo "$@"
    fi
}

printf_verb () {
    if [ "x$verbose" != "x" ]; then
	printf "$@"
    fi
}

run_and_time () {
    echo_verb "  $1:"
    shift
    time { "$@"; } 2>&1
}

make_parsed_files () {
    year=$1
    run_and_time "adding parses and lemgrams" \
	$scriptdir/vrt-add-parses.py --database $dbdir/db$year.sqlite \
	--input-dir $orig_vrt_dir/$year --output-dir $parsed_vrt_dir \
	--lemgram-pos-map-file $lemgram_posmap
}

make_cwb () {
    year=$1
    corpname=klk_fi_$year
    corpname_u=`echo $corpname | sed -e 's/.*/\U&\E/'`
    corpdatadir=$corproot/data/$corpname
    regfile=$regdir/$corpname
    rm $regfile $corpdatadir/*
    run_and_time "encoding for CWB" \
	$cwb_encode -d $corpdatadir -R $regfile -xsB -c utf8 \
	$struct_attrs $pos_attrs -F $parsed_vrt_dir/$year
    run_and_time "making CWB indices" \
	$cwb_make -r $regdir -g korp -M 2000 $corpname_u
    run_and_time "extracting info" \
	$scriptdir/cwbdata-extract-info.sh --cwbdir $cwbdir --registry $regdir \
	--update $corpname
}

years=$*

for year in $years; do
    echo_verb "* $year:"
    if [ -d $parsed_vrt_dir/$year ]; then
	echo "$year already parsed; skipping"
    elif [ ! -r $dbdir/db$year.sqlite ]; then
	echo "Parse database file $dbdir/db$year.sqlite not found"
    else
	make_parsed_files $year
	make_cwb $year
    fi
done
