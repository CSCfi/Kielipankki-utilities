#! /bin/bash

# Start s24-json-extract-ids.py jobs on the Taito batch system with
# estimated time and memory limits.
#
# Usage: sbatch-s24-json-extract-ids.sh s24_data.json ...
#
# Jyrki Niemi, FIN-CLARIN, 2017-11-24


progname=$(basename $0)
progdir=$(dirname $0)

log_dir=log
action=sbatch

mkdir -p $log_dir

make_sbatch () {
    local ifn=$1
    local basefn=$(basename $ifn .json)
    local ofn=${basefn}_ids.tsv
    if [ -s $ofn ]; then
	echo "Skipping $ifn: $ofn already exists"
	return
    else
	echo "$ifn"
    fi
    local filesize=$(ls -l $ifn | awk '{print $5}')
    local memory=$(($filesize * 10 / 1024 / 1024))
    local timelimit=$((filesize / 1024 / 1024 / 100 + 1))
    $action <<EOF
#! /bin/bash -l
#SBATCH -J extrids_$basefn
#SBATCH -o $log_dir/s24_extrids_log-${basefn}-%j.out
#SBATCH -e $log_dir/s24_extrids_log-${basefn}-%j.err
#SBATCH -t $timelimit
#SBATCH --mem-per-cpu $memory
#SBATCH -n 1
#SBATCH -p serial

echo Job: \$SLURM_JOB_ID \$SLURM_JOB_NAME
echo Input: $ifn
$progdir/s24-json-extract-ids.py $ifn > $ofn
EOF
}

for fname in "$@"; do
    make_sbatch $fname
done
