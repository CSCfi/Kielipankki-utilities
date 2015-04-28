#! /bin/bash

date +'Start: %F %T %s.%N'

opts=
if [ "x$1" = "x--new" ]; then
    opts="--output-type=new-strings --include-word-forms"
    shift
fi

year=$1
echo Year: $year
topdir=$WRKDIR/corpora/vrt/klk_fi_parsed
cd $topdir
rels_tar=out/klk_fi_${year}_rels.tar

if [ ! -e $rels_tar ]; then
    module load python-env/2.7.6
    mkdir -p out/$year

    tar xzOf in/klk_fi_${year}_parsed_vrt.tgz --wildcards $year/\*.vrt |
    /proj/clarin/korp/scripts/vrt-extract-relations.py \
	--input-fields 'word lemma lemmacomp pos msd dephead deprel ref ocr lex' \
	--relation-map in/wordpict_relmap_tdt.tsv \
	--output-prefix out/$year/klk_fi_${year}_rels \
	$opts
    # --sort --compress=gzip --temporary-files
    # Sorting and compressing files within vrt-extract-relations.py
    # often seems to leave the rels_sentences file incomplete. Why?
    for f in out/$year/*.tsv; do
	mv $f $f.unsorted
	sort_opts=
	case $f in
	    *_rels.tsv | *_rels_sentences.tsv | *_rels_strings.tsv )
		sort_opts=-n
		;;
	esac
	sort $sort_opts $f.unsorted | gzip > $f.gz
    done
    # tar cpf $rels_tar -C out --wildcards $year/\*.gz
    # Wildcards do not seem to work in tar even with --wildcards. Why?
    (
	cd out
	tar cpf ../$rels_tar --wildcards $year/*.gz
    )
fi

date +'End: %F %T %s.%N'
