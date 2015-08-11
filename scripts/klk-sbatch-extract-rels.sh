#! /bin/bash

progdir=`dirname $0`
basedir=/wrk/jyniemi/corpora/vrt/klk_fi_parsed

ls -lS $basedir/in/klk_fi*.tgz |
gawk '{printf "%2d\t%s\n", log($5)/log(2)+1, gensub("[^0-9]+", "", "g", $8)}' > $basedir/all_years.txt

action=sbatch
if [ "x$1" = "x--dry-run" ] || [ "x$1" = "x-n" ]; then
    action=cat
    shift
fi

if [ "x$1" != x ]; then
    sizes="$*"
else
    sizes=`cut -f1 $basedir/all_years.txt | sort -u`
fi

runner_opts="--input-fields 'word lemma lemmacomp pos msd dephead deprel ref ocr lex' --relation-map $basedir/in/wordpict_relmap_tdt.tsv --keep-temp-files"

for size in $sizes; do
    rm -f $basedir/years_$size.txt
    for year in `egrep "^$size" $basedir/all_years.txt | cut -f2`; do
	if [ ! -e $basedir/out/klk_fi_${year}_rels.tar ]; then
	    echo $year >> $basedir/years_$size.txt
	fi
    done
done

for size in $sizes; do
    if [ -s $basedir/years_$size.txt ]; then
	name=extrels_klk_$size
	num=`wc -l < $basedir/years_$size.txt`
	mins=`gawk 'BEGIN {a = 2 ** ('$size' - 20) / 10 + 1; printf "%d", a}'`
	mem=`gawk 'BEGIN {a = 2 ** ('$size' - 14) * 1.25; if (a < 128) {a = 128} if (a > 128000) {a = 128000}; print a}'`
	$action <<EOF
#! /bin/bash -l
#SBATCH -J $name
#SBATCH -o $basedir/log/${name}_%A_%a.out
#SBATCH -e $basedir/log/${name}_%A_%a.err
#SBATCH -t $mins
#SBATCH --mem-per-cpu $mem
#SBATCH --array=1-$num
#SBATCH -n 1
#SBATCH -p serial

year=\$(sed -n "\$SLURM_ARRAY_TASK_ID"p $basedir/years_$size.txt)
echo Job: \$SLURM_JOB_ID \$SLURM_JOB_NAME
tar xzOf $basedir/in/klk_fi_\${year}_parsed_vrt.tgz --wildcards \$year/\*.vrt |
$progdir/run-extract-rels.sh $runner_opts --corpus-name klk_fi_\$year \
    --output-dir $basedir/out/\$year
mv $basedir/out/\$year/*.tar $basedir/out
EOF
    fi
done
