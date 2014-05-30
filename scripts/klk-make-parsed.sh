#! /bin/bash
# -*- coding: utf-8 -*-

# Make a parsed version of the Finnish National Library corpus


progname=`basename $0`
progdir=`dirname $0`

setvar_host () {
    varname=$1
    localval=$2
    otherval=$3
    case $HOSTNAME in
	*.csc.fi )
	    val=$otherval
	    ;;
	* )
	    val=$localval
	    ;;
    esac
    eval $varname=$val
}

setvar_host host local csc
corproot_final=/v/corpora
setvar_host corproot $corproot_final /wrk/jyniemi/corpora
regdir=$corproot/registry
vrtdir=$corproot/vrt
orig_vrt_dir=$vrtdir/klk_fi
parsed_vrt_dir=$vrtdir/klk_fi_parsed
setvar_host dbdir $corproot/conll09 /wrk/jpiitula
setvar_host cwbroot /usr/local/cwb /fs/proj1/kieli/korp/cwb
cwbdir=$cwbroot/bin

cwb_encode=$cwbdir/cwb-encode
setvar_host cwb_make /usr/local/bin/cwb-make $cwbdir/cwb-make
cwb_describe_corpus=$cwbdir/cwb-describe-corpus
scriptdir=$progdir
lemgram_posmap=$parsed_vrt_dir/lemgram_posmap_tdt.txt

stagedir=$parsed_vrt_dir/stages
stage_fname_templ=$stagedir/klk_fi_%s.stages

mkdir -p $stagedir

setvar_host group korp clarin

setvar_host skip_stages "" "*-load"

if [ "$host" = "csc" ]; then
    export PERL5LIB=$cwbroot/share/perl5
fi

struct_attrs='-S text:0+issue_date+sentcount+language+elec_date+dateto+datefrom+img_url+label+publ_part+issue_no+tokencount+part_name+publ_title+publ_id+page_id+page_no+issue_title -S paragraph:0+id -S sentence:0+local_id+parse_state+id'
pos_attrs='-P lemma -P lemmacomp -P pos -P msd -P dephead -P deprel -P ref -P ocr -P lex'

verbose=1

export TIMEFORMAT="    %U + %S s (real %R s)"


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
    stage_file=$1
    stage_label=$2
    echo $stage_label >> $stage_file
}

stage_is_completed () {
    stage_file=$1
    stage_label=$2
    if [ ! -e $stage_file ]; then
	touch $stage_file
	return 1
    fi
    grep -Eq "^$stage_label"'$' $stage_file
}

run_and_time () {
    year=$1
    stage_label=$2
    echo_text=$3
    shift; shift; shift
    stage_file=`printf $stage_fname_templ $year`
    printf_verb "  $echo_text: "
    if stage_is_completed $stage_file $stage_label; then
	echo_verb "already done"
	return
    elif [ "x$skip_stages" != "x" ]; then
	case $stage_label in
	    $skip_stages )
		echo_verb "skipping"
		return
		;;
	esac
    fi
    echo_verb ""
    time { "$@"; } 2>&1
    if [ $? = 0 ]; then
	add_stage $stage_file $stage_label
    else
	error "an error occurred when $echo_text; aborting"
    fi
}

make_parsed_files () {
    year=$1
    database=$2
    run_and_time $year parses-added "adding parses and lemgrams" \
	$scriptdir/vrt-add-parses.py --database $database \
	--input-dir $orig_vrt_dir/$year --output-dir $parsed_vrt_dir \
	--lemgram-pos-map-file $lemgram_posmap
}

cwb_encode () {
    year=$1
    corpdatadir=$2
    regfile=$3
    rm -f $regfile $corpdatadir/*
    if [ ! -d $corpdatadir ]; then
	mkdir -p $corpdatadir
    fi
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
	$cwb_make -r $regdir -g $group -p 664 -M 2000 $corpname_u
    run_and_time $year info-extracted "extracting info" \
	$scriptdir/cwbdata-extract-info.sh --cwbdir $cwbdir --registry $regdir \
	--update $corpname
    # # The corpus path cannot be changed here if we want to get the
    # # statistics with cwb-describe-corpus
    # if [ "$corproot" != "$corproot_final" ]; then
    # 	sed -i.bak -e "s|$corproot|$corproot_final|g" $regfile
    # fi
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

yeardbs=$*

for yeardb in $yeardbs; do
    case $yeardb in
	*.sqlite )
	    yeardb_file=$yeardb
	    ;;
	* )
	    yeardb_file=$dbdir/db$yeardb.sqlite
	    ;;
    esac
    if [ ! -r $yeardb_file ]; then
	echo "Warning: parse database file $yeardb_file not found"
	if [ $yeardb != $yeardb_file ] &&
	    stage_is_completed `printf $stage_fname_templ $yeardb` parses-added
	then
	    echo "Parses already added to year $yeardb; trying to continue"
	    years=$yeardb
	else
	    continue
	fi
    else
	years=`sqlite3 $yeardb_file 'select distinct yno from doc;'`
    fi
    for year in $years; do
	echo_verb "$year:"
	{ 
	    time {
		make_parsed_files $year $yeardb_file
		make_cwb $year
	    } 2>&1
	} 2> $parsed_vrt_dir/$progname.$$.times
	if [ "x$verbose" != "x" ]; then
	    print_stats $year "$(cat $parsed_vrt_dir/$progname.$$.times)"
	fi
	rm $parsed_vrt_dir/$progname.$$.times
    done
done
