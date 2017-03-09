#! /bin/bash
# -*- coding: utf-8 -*-

# Make a parsed version of the Swedish part of the Finnish National Library
# corpus.
# The input is parsed VRT files, output CWB files and lemgram TSV files.


progname=`basename $0`
progdir=`dirname $0`

setvar_host () {
    varname=$1
    localval=$2
    otherval=$3
    # The Taito compute nodes do not seem to have a fully qualified
    # hostname; recognize that case from SLURM_JOB_ID
    if [ "x$SLURM_JOB_ID" != x ]; then
	val=$otherval
    else
	case $HOSTNAME in
	    *.csc.fi )
		val=$otherval
		;;
	    * )
		val=$localval
		;;
	esac
    fi
    eval $varname="'$val'"
}

corpname_prefix=klk_sv
corpname_prefix_u=KLK_SV

setvar_host host local csc
corproot_final=/v/corpora
setvar_host corproot $corproot_final /wrk/jyniemi/corpora
regdir=$corproot/registry
vrtdir=$corproot/vrt
tsvdir=$corproot/sql
parsed_vrt_dir=$vrtdir/$corpname_prefix/parsed
setvar_host cwbroot /usr/local/cwb $USERAPPL
cwbdir=$cwbroot/bin

cwb_encode=$cwbdir/cwb-encode
setvar_host cwb_make /usr/local/bin/cwb-make $cwbdir/cwb-make
cwb_describe_corpus=$cwbdir/cwb-describe-corpus
scriptdir=$progdir

stagedir=$parsed_vrt_dir/stages
stage_fname_templ=$stagedir/${corpname_prefix}_%s.stages

mkdir -p $stagedir

setvar_host group korp clarin

setvar_host skip_stages "*-load" "*-load"

if [ "$host" = "csc" ]; then
    export PERL5LIB=$cwbroot/share/perl5
fi

struct_attrs='-S text:0+issue_date+sentcount+language+elec_date+dateto+datefrom+img_url+label+publ_part+issue_no+tokencount+part_name+publ_title+publ_id+page_id+page_no+issue_title+file -S paragraph:0+n -S sentence:0+id+n'
pos_attrs='-P ocr -P style -P pos -P msd -P lemma/ -P lex/ -P saldo/ -P prefix/ -P suffix/ -P ref -P dephead -P deprel'

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
	for skip_stage in $skip_stages; do
	    case $stage_label in
		$skip_stage )
		    echo_verb "skipping"
		    return
		    ;;
	    esac
	done
    fi
    echo_verb ""
    time { "$@"; } 2>&1
    if [ $? = 0 ]; then
	add_stage $stage_file $stage_label
    else
	error "an error occurred when $echo_text; aborting"
    fi
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
    corpname=${corpname_prefix}_$year
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

make_lemgrams_tsv () {
    year=$1
    for f in $parsed_vrt_dir/$year/*.vrt; do
	cat $f
    done |
    $scriptdir/vrt-extract-lemgrams.sh \
	--corpus-name ${corpname_prefix_u}_$year \
	--lemgram-field 7 --prefix-field 9 --suffix-field 10 |
    gzip > $tsvdir/${corpname_prefix}_${year}_lemgrams.tsv.gz
}

make_databases () {
    year=$1
    run_and_time $year lemgrams-tsv "extracting lemgrams for database" \
	make_lemgrams_tsv $year
}

print_stats () {
    year=$1
    times=$2
    total_time=`echo $times | awk '{print $1 + $3}'`
    if [ "x$total_time" != "x" ]; then
	echo_verb "  total:"$times
	if [ "$total_time" != "0" ]; then
	    $cwb_describe_corpus -r $regdir -s ${corpname_prefix}_$year |
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
    {
	time {
	    make_cwb $year
	    make_databases $year
	} 2>&1
    } 2> $parsed_vrt_dir/$progname.$$.times
    if [ "x$verbose" != "x" ]; then
	print_stats $year "$(cat $parsed_vrt_dir/$progname.$$.times)"
    fi
    rm $parsed_vrt_dir/$progname.$$.times
done
