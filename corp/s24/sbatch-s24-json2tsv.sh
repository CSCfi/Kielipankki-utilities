#! /bin/bash

# Start s24-json2tsv.py jobs on the Taito batch system with estimated
# time and memory limits.
#
# Usage: sbatch-s24-json2tsv.sh s24_data.json ...
#
# Jyrki Niemi, FIN-CLARIN, 2017-11-27


progname=$(basename $0)
progdir=$(dirname $0)

log_dir=log
action=sbatch

mkdir -p $log_dir

make_sbatch () {
    local ifn=$1
    local basefn=$(basename $ifn .json)
    local ofn=tsv/${basefn}.tsv
    if [ -s $ofn ]; then
	echo "Skipping $ifn: $ofn already exists"
	return
    else
	echo "$ifn"
    fi
    local filesize=$(ls -l $ifn | awk '{print $5}')
    local memory=$(($filesize * 12 / 1024 / 1024))
    local timelimit=$((filesize / 1024 / 1024 / 50 + 1))
    $action <<EOF
#! /bin/bash -l
#SBATCH -J json2tsv_$basefn
#SBATCH -o $log_dir/s24_json2tsv_log-${basefn}-%j.out
#SBATCH -e $log_dir/s24_json2tsv_log-${basefn}-%j.err
#SBATCH -t $timelimit
#SBATCH --mem-per-cpu $memory
#SBATCH -n 1
#SBATCH -p serial

echo Job: \$SLURM_JOB_ID \$SLURM_JOB_NAME
echo Input: $ifn
env PYTHONPATH=/proj/clarin/korp/scripts $progdir/s24-json2tsv.py $ifn > $ofn
EOF
}

for fname in "$@"; do
    make_sbatch $fname
done
