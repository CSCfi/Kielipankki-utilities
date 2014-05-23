#! /bin/bash
# -*- coding: utf-8 -*-

# Make a parsed version of the Finnish National Library corpus


progname=`basename $0`

corproot=/v/corpora
regdir=$corproot/registry
vrtdir=$corproot/vrt
orig_vrt_dir=$vrtdir/klk_fi
parsed_vrt_dir=$vrtdir/klk_fi_parsed
dbdir=$corproot/conll09
cwbdir=/usr/local/cwb/bin

cwb_encode=$cwbdir/cwb-encode
cwb_make=/usr/local/bin/cwb-make
cwb_describe_corpus=$cwbdir/cwb-describe-corpus
scriptdir=/home/janiemi/finclarin/korp-git/corp/scripts
lemgram_posmap=$parsed_vrt_dir/lemgram_posmap_tdt.txt
stage_file=$parsed_vrt_dir/klk-make-parsed-stages.txt

struct_attrs='-S text:0+issue_date+sentcount+language+elec_date+dateto+datefrom+img_url+label+publ_part+issue_no+tokencount+part_name+publ_title+publ_id+page_id+page_no+issue_title -S paragraph:0+id -S sentence:0+local_id+parse_state+id'
pos_attrs='-P lemma -P lemmacomp -P pos -P msd -P dephead -P deprel -P ref -P ocr -P lex'

verbose=1

export TIMEFORMAT="    %U + %S s (real %R s)"

if [ ! -e $stage_file ]; then
    touch $stage_file
fi


error () {
    echo "$@" >&2
    exit 1
}

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

add_stage () {
    year=$1
    stage_label=$2
    old_stages=`grep -E "^$year " $stage_file || echo "$year"`
    {
	grep -Ev "^$year " $stage_file
	echo "$old_stages $stage_label"
    } > $stage_file.new
    mv $stage_file.new $stage_file
}

run_and_time () {
    year=$1
    stage_label=$2
    echo_text=$3
    shift; shift; shift
    printf_verb "  $echo_text: "
    if grep -Eq "^$year .*\b$stage_label\b" $stage_file; then
	echo_verb "already done"
    else
	echo_verb ""
	time { "$@"; } 2>&1
	if [ $? = 0 ]; then
	    add_stage $year $stage_label
	else
	    error "an error occurred when $echo_text; aborting"
	fi
    fi
}

make_parsed_files () {
    year=$1
    run_and_time $year parses-added "adding parses and lemgrams" \
	$scriptdir/vrt-add-parses.py --database $dbdir/db$year.sqlite \
	--input-dir $orig_vrt_dir/$year --output-dir $parsed_vrt_dir \
	--lemgram-pos-map-file $lemgram_posmap
}

cwb_encode () {
    year=$1
    corpdatadir=$2
    regfile=$3
    rm $regfile $corpdatadir/*
    $cwb_encode -d $corpdatadir -R $regfile -xsB -c utf8 \
	$struct_attrs $pos_attrs -F $parsed_vrt_dir/$year
}

make_cwb () {
    year=$1
    corpname=klk_fi_$year
    corpname_u=`echo $corpname | sed -e 's/.*/\U&\E/'`
    corpdatadir=$corproot/data/$corpname
    regfile=$regdir/$corpname
    run_and_time $year cwb-encoded "encoding for CWB" \
	cwb_encode $year $corpdatadir $regfile
    run_and_time $year cwb-indexed "making CWB indices" \
	$cwb_make -r $regdir -g korp -M 2000 $corpname_u
    run_and_time $year info-extracted "extracting info" \
	$scriptdir/cwbdata-extract-info.sh --cwbdir $cwbdir --registry $regdir \
	--update $corpname
}

print_stats () {
    year=$1
    times=$2
    total_time=`echo $times | awk '{print $1 + $3}'`
    if [ "x$total_time" != "x" ]; then
	echo_verb "  total:"$times
	if [ "$total_time" != "0" ]; then
	    $cwb_describe_corpus -r $regdir -s klk_fi_$year |
	    awk 'BEGIN { time = ARGV[1]; ARGV[1] = "" }
		 /^.-ATT (word|sentence)\>/ { cnt[$2] = $3 }
		 END { 
		     types[1] = "word"; types[2] = "sentence";
		     for (i in types) {
			 printf "  %ss: %d (%.2f/s)\n", types[i], \
                                cnt[types[i]], cnt[types[i]] / time 
		     }
		 }' \
		     $total_time
	fi
    fi
}

years=$*

for year in $years; do
    echo_verb "$year:"
    if [ ! -r $dbdir/db$year.sqlite ]; then
	echo "Parse database file $dbdir/db$year.sqlite not found"
    else
	{ 
	    time {
		make_parsed_files $year
		make_cwb $year
	    } 2>&1
	} 2> $parsed_vrt_dir/$progname.$$.times
	if [ "x$verbose" != "x" ]; then
	    print_stats $year "$(cat $parsed_vrt_dir/$progname.$$.times)"
	fi
	rm $parsed_vrt_dir/$progname.$$.times
    fi
done
