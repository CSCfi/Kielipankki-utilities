#! /bin/bash

scriptdir=`dirname $0`

ls -lS klk_fi*.tgz |
gawk '{printf "%2d\t%s\n", log($5)/log(2)+1, gensub("[^0-9]+", "", "g", $8)}' > all_years.txt

if [ "x$1" != x ]; then
    sizes="$*"
else
    sizes=`cut -f1 all_years.txt | sort -u`
fi

for size in $sizes; do
    rm -f years_$size.txt
    for year in `egrep "^$size" all_years.txt | cut -f2`; do
	if [ ! -e $scriptdir/klk_fi_${year}_rels.tar ]; then
	    echo $year >> years_$size.txt
	fi
    done
done

for size in $sizes; do
    if [ -s years_$size.txt ]; then
	name=rels_$size
	num=`wc -l < years_$size.txt`
	mins=`gawk 'BEGIN {a = 2 ** ('$size' - 20) / 20 + 1; printf "%d", a}'`
	mem=`gawk 'BEGIN {a = 2 ** ('$size' - 15); if (a < 128) {a = 128} if (a > 64000) {a = 64000}; print a}'`
	sbatch <<EOF
#! /bin/bash
#SBATCH -J $name
#SBATCH -o ${name}_%A_%a.out
#SBATCH -e ${name}_%A_%a.err
#SBATCH -t $mins
#SBATCH --mem-per-cpu $mem
#SBATCH --array=1-$num
#SBATCH -n 1
#SBATCH -p serial

cd $scriptdir
year=\$(sed -n "\$SLURM_ARRAY_TASK_ID"p years_$size.txt)
./run-extract-rels.sh \$year
EOF
    fi
done
