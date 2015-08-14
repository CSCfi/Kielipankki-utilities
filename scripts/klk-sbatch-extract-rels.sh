#! /bin/bash

progdir=`dirname $0`
progname=`basename $0`
basedir=/wrk/jyniemi/corpora/vrt/klk_fi_parsed

shortopts="hnc:f:r:i:o:l:t:v"
longopts="help,dry-run,timelimit:,memory:,timelimit-factor:,memory-factor:,verbose"

action=sbatch
timelimit=
memory=
timelimit_factor=100
memory_factor=100

. $progdir/korp-lib.sh


usage () {
    cat <<EOF
Usage: $progname [options]

Subtmit a SLURM batch job to extract dependency relations from the KLK
corpora for the Korp word picture.

Options:
  -h, --help
  -n, --dry-run
  --timelimit MINS
  --memory MB
  --timelimit-factor PERCENTAGE
  --memory-factor PERCENTAGE
  -v, --verbose
EOF
    exit 0
}

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	-n | --dry-run )
	    action=cat
	    ;;
	--timelimit )
	    timelimit=$2
	    shift
	    ;;
	--memory )
	    memory=$2
	    shift
	    ;;
	--timelimit-factor )
	    timelimit_factor=$2
	    shift
	    ;;
	--memory-factor )
	    memory_factor=$2
	    shift
	    ;;
	-v | --verbose )
	    verbose=1
	    ;;
	-- )
	    shift
	    break
	    ;;
	--* )
	    warn "Unrecognized option: $1"
	    ;;
	* )
	    break
	    ;;
    esac
    shift
done

ls -lS $basedir/in/klk_fi*.tgz |
gawk '{printf "%2d\t%s\n", log($5)/log(2)+1, gensub("[^0-9]+", "", "g", $8)}' > $basedir/all_years.txt

if [ "x$1" != x ]; then
    sizes="$*"
else
    sizes=`cut -f1 $basedir/all_years.txt | sort -u`
fi

runner_opts="--input-fields 'word lemma lemmacomp pos msd dephead deprel ref ocr lex' --relation-map $basedir/in/wordpict_relmap_tdt.tsv --optimize-memory --verbose"

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
	if [ "x$timelimit" = x ]; then
	    timelimit=`gawk 'BEGIN {a = (2 ** ('$size' - 19) / 10 + 1) * '$timelimit_factor' / 100; printf "%d", a}'`
	fi
	if [ "x$memory" = x ]; then
	    memory=`gawk 'BEGIN {a = (2 ** ('$size' - 15)) * '$memory_factor' / 100; if (a < 32) {a = 32} if (a > 128000) {a = 128000}; printf "%d", a}'`
	fi
	if [ "x$verbose" != x ]; then
	    cat <<EOF
Batch job "$name" to partition "serial"
Max run time: $timelimit mins
RAM per CPU: $memory MiB
Years: $(cat $basedir/years_$size.txt | tr '\n' ' ')
EOF
	fi
	$action <<EOF
#! /bin/bash -l
#SBATCH -J $name
#SBATCH -o $basedir/log/${name}_%A_%a.out
#SBATCH -e $basedir/log/${name}_%A_%a.err
#SBATCH -t $timelimit
#SBATCH --mem-per-cpu $memory
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
